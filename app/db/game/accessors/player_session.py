from typing import Optional, List
from time import time_ns

from sqlalchemy.dialects.postgresql import insert

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *


class PlayerSessionAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def get_current_player_session(self, 
            user_id: int, chat_id: int) -> Optional[PlayerSession]:
        return await PlayerSession.load(
            player=Player.load(
                user_profile=UserProfile
            ),
            game_session=GameSession,
            add_player_dataport=PlayerDataport
        ).where(
            db.and_(
                UserProfile.vk_id == user_id,
                GameSession.chat_id == chat_id,
                GameSession.state.notin_([
                    GameSessionState.CLOSED,
                    GameSessionState.TERMINATED,
                ]),
            )
        ).gino.one_or_none()

    async def get_dealing_players(self, game_session: GameSession) -> List[PlayerSession]:
        return await PlayerSession.load(
            player=Player.load(
                user_profile=UserProfile
            ),
            add_player_dataport=PlayerDataport
        ).where(
            db.and_(
                PlayerSession.game_session_id == game_session.id,
                Player.vk_id != self.app.config.bot.group_id,
                PlayerSession.state.in_([
                    PlayerSessionState.INITIAL_DEAL,
                    PlayerSessionState.DEALING,
                ])
            )
        ).gino.all()

    async def get_broken_out_players(self, 
            game_session: GameSession) -> List[PlayerSession]:
        return await PlayerSession.load(
            player=Player.load(
                user_profile=UserProfile
            ),
            add_player_dataport=PlayerDataport
        ).where(
            db.and_(
                PlayerSession.game_session_id == game_session.id,
                # Player.vk_id != self.app.config.bot.group_id,
                PlayerSession.state.in_([
                    PlayerSessionState.STANDING,
                    PlayerSessionState.BUSTED,
                    PlayerSessionState.BLACKJACKED,
                ])
            )
        ).gino.all()
    
    async def take_player_bet(self, player_session: PlayerSession, bet: int) -> bool:
        async with self.app.database.orm.transaction() as tx:
            player = await Player.update.where(
                Player.id == player_session.player.id
            ).values(
                money=Player.money - bet
            ).returning(Player.money).gino.one()

            if player.money < 0:
                tx.raise_rollback()
                return False

            await player_session.update(
                state=PlayerSessionState.INITIAL_DEAL,
                bet=bet,
                timestamp=time_ns()
            ).apply()

            return True
    
    async def return_player_bet(self, player_session: PlayerSession) -> None:
        async with self.app.database.orm.transaction() as tx:
            await player_session.player.update(
                money=Player.money + (player_session.bet or 0)
            ).apply()

            await player_session.update(
                state=PlayerSessionState.CUTOUT,
                timestamp=time_ns()
            ).apply()

    async def update_timestamp(self, player_session: PlayerSession) -> None:
        await player_session.update(
            timestamp=time_ns()
        ).apply()

    async def break_out_player(self, player_session: PlayerSession, 
                                            breakout_reason: str) -> None:
        player_states = {
            "bust": PlayerSessionState.BUSTED,
            "blackjack": PlayerSessionState.BLACKJACKED,
            "stand": PlayerSessionState.STANDING,
        }
        await player_session.update(
            state=player_states[breakout_reason],
            timestamp=time_ns()
        ).apply()

    async def pay_out_player(self, player_session: PlayerSession, 
                                            payout_ratio: int) -> None:
        async with self.app.database.orm.transaction() as tx:
            gain = player_session.bet * payout_ratio
            await player_session.player.update(
                money=Player.money + gain
            ).apply()

            await player_session.update(
                state=PlayerSessionState.PAIDOUT,
                payout_ratio=payout_ratio,
                timestamp=time_ns()
            ).apply()

    async def cut_out_player(self, player_session: PlayerSession) -> None:
        await player_session.update(
            state=PlayerSessionState.CUTOUT,
            timestamp=time_ns()
        ).apply()