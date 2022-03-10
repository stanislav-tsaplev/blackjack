from typing import Optional, List

from sqlalchemy.dialects.postgresql import insert

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *


class PlayerSessionAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def create_dealer_session(self, game_session: GameSession) -> PlayerSession:
        await insert(UserProfile).values(
            vk_id=self.app.config.bot.group_id,
            first_name="Dealer",
            last_name=self.app.config.bot.name,
        ).on_conflict_do_nothing().gino.status()
        
        await insert(Player).values(
            vk_id=self.app.config.bot.group_id,
            chat_id=game_session.chat_id
        ).on_conflict_do_nothing().gino.status()

        dealer = await Player.query.where(
            db.and_(
                Player.vk_id == self.app.config.bot.group_id,
                Player.chat_id == game_session.chat_id
            )
        ).gino.one()
        
        return await PlayerSession.create(
            game_session_id=game_session.id,
            player_id=dealer.id
        )

    async def get_dealer_session(self, chat_id: int) -> Optional[PlayerSession]:
        return await PlayerSession.load(
            game_session=GameSession,
            player=Player.load(
                user_profile=UserProfile
            ),
            add_player_dataport=PlayerDataport
        ).where(
            db.and_(
                UserProfile.vk_id == self.app.config.bot.group_id,
                GameSession.chat_id == chat_id,
                GameSession.state == GameSessionState.OPENED,
            )
        ).gino.one_or_none()

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
                GameSession.state == GameSessionState.OPENED,
            )
        ).gino.one_or_none()

    async def get_waiting_players(self, game_session: GameSession) -> List[PlayerSession]:
        return await PlayerSession.load(
            player=Player.load(
                user_profile=UserProfile
            ),
            add_player_dataport=PlayerDataport
        ).where(
            db.and_(
                PlayerSession.game_session_id == game_session.id,
                PlayerSession.state == PlayerSessionState.WAITING,
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
                PlayerSession.state.in_([
                    PlayerSessionState.STANDING,
                    PlayerSessionState.BUSTED,
                    PlayerSessionState.BLACKJACKED,
                ])
            )
        ).gino.all()
    
    async def take_player_bet(self, player_session: PlayerSession, bet: int) -> None:
        await player_session.update(bet=bet, state=PlayerSessionState.WAITING).apply()

    async def break_out_player(self, player_session: PlayerSession, 
                                            breakout_reason: str) -> None:
        player_states = {
            "bust": PlayerSessionState.BUSTED,
            "blackjack": PlayerSessionState.BLACKJACKED,
            "stand": PlayerSessionState.STANDING,
        }
        await player_session.update(state=player_states[breakout_reason]).apply()

    async def pay_out_player(self, player_session: PlayerSession, 
                                            payout_ratio: int) -> None:
        async with self.app.database.orm.transaction() as tx:
            await player_session.update(
                state=PlayerSessionState.PAIDOUT,
                payout_ratio=payout_ratio
            ).apply()

            profit = player_session.bet * (payout_ratio - 1)
            await player_session.player.update(
                money=Player.money + profit
            ).apply()

    async def cut_out_player(self, player_session: PlayerSession) -> None:
        await player_session.update(state=PlayerSessionState.CUTOUT).apply()