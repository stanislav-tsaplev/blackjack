from typing import Optional, List
from datetime import datetime
from time import time_ns

from sqlalchemy.dialects.postgresql import insert

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *


INITIAL_MONEY_SUM = 1000

class GameSessionAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def has_current_game_session(self, chat_id: int) -> Optional[GameSession]:
        current_game_session = await GameSession.query.where(
            db.and_(
                GameSession.chat_id == chat_id,
                GameSession.state == GameSessionState.OPENED
            )
        ).gino.one_or_none()
        return current_game_session is not None

    async def get_current_game_session(self, chat_id: int) -> Optional[GameSession]:
        game_session = await GameSession.distinct(GameSession.id).load(
                add_player_session=PlayerSession.load(
                    player=Player.load(
                        user_profile=UserProfile
                    )
                )
            ).where(
                db.and_(
                    GameSession.chat_id == chat_id,
                    GameSession.state == GameSessionState.OPENED
                )
            ).gino.one_or_none()
        return game_session

    async def create_game_session(self, chat_id: int, 
                                        user_profiles: List[UserProfile]) -> GameSession:
        async with self.app.database.orm.transaction() as tx:
            await insert(GameChat).values(
                [
                    {
                        "chat_id": chat_id
                    }
                ]
            ).on_conflict_do_nothing().gino.status()

            await insert(UserProfile).values(
                [
                    {
                        "vk_id": self.app.config.bot.group_id,
                        "first_name": "Dealer",
                        "last_name": self.app.config.bot.name,
                    }  
                ] + [
                    {
                        "vk_id": user_profile.vk_id,
                        "first_name": user_profile.first_name,
                        "last_name": user_profile.last_name
                    }
                    for user_profile in user_profiles
                ]
            ).on_conflict_do_nothing().gino.status()
            
            await insert(Player).values(
                [
                    {
                        "vk_id": self.app.config.bot.group_id,
                        "chat_id": chat_id,
                    }
                ] + [
                    {
                        "vk_id": user_profile.vk_id,
                        "chat_id": chat_id,
                        "money": INITIAL_MONEY_SUM
                    }
                    for user_profile in user_profiles
                ]
            ).on_conflict_do_nothing().gino.status()

            dealer = await Player.query.where(
                db.and_(
                    Player.chat_id == chat_id,
                    Player.vk_id == self.app.config.bot.group_id
                )
            ).gino.one()

            players = await Player.query.where(
                db.and_(
                    Player.chat_id == chat_id,
                    Player.vk_id.in_([user_profile.vk_id 
                                        for user_profile in user_profiles]
                    ),
                )
            ).gino.all()

            game_session = await GameSession.create(
                chat_id=chat_id,
                started_at=datetime.utcnow()   # TODO: подружить freezegun с offset-aware datetime
            )
            
            dealer_session = await PlayerSession.create(
                player_id = dealer.id,
                game_session_id = game_session.id,
            )

            player_sessions = await PlayerSession.insert().values(
                [
                    {
                        "player_id": player.id,
                        "game_session_id": game_session.id,
                        "timestamp": time_ns()
                    }
                    for player in players
                ]
            ).returning(PlayerSession.id).gino.all()
            
            await PlayerDataport.insert().gino.all([
                {
                    "player_session_id": player_session.id,
                } 
                for player_session in player_sessions
            ])

        return await GameSession.distinct(GameSession.id).load( 
            add_player_session=PlayerSession.load(
                player=Player.load(
                    user_profile=UserProfile
                ),
                add_player_dataport=PlayerDataport
            )
        ).where(
            GameSession.id == game_session.id
        ).gino.one()

    async def close_game_session(self, game_session: GameSession):
        await game_session.update(
            state=GameSessionState.CLOSED,
            closed_at=datetime.utcnow()
        ).apply()

    async def terminate_game_session(self, game_session: GameSession):
        async with self.app.database.orm.transaction() as tx:
            for player_session in game_session.player_sessions:
                await self.app.db_store.player_sessions.return_player_bet(player_session)

            await game_session.update(
                state=GameSessionState.TERMINATED,
                closed_at=datetime.utcnow()
            ).apply()