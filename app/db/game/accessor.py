from datetime import datetime
from typing import Optional, List

from sqlalchemy.dialects.postgresql import insert

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *
from app.vk_api.models import VkApiMemberProfile


class GameAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def get_current_game_session(self, chat_id: int) -> Optional[GameSession]:
        game_session = await GameSessionModel.query \
            .where(GameSessionModel.chat_id == chat_id) \
            .where(GameSessionModel.state == GameSessionState.OPENED) \
            .gino.one_or_none()
        return game_session

    async def create_game_session(self, chat_id: int, 
        user_profiles: List[VkApiMemberProfile]) -> GameSession:

        async with self.app.database.orm.transaction() as tx:
            await insert(GameChatModel).values([
                {
                    "chat_id": chat_id
                }
            ]).on_conflict_do_nothing().gino.all()

            await insert(UserModel).values([
                {
                    "vk_id": user_profile.id,
                    "first_name": user_profile.first_name,
                    "last_name": user_profile.last_name
                }
                for user_profile in user_profiles
            ]).on_conflict_do_nothing().gino.all()
            
            await insert(PlayerModel).values([
                {
                    "vk_id": user_profile.id,
                    "chat_id": chat_id
                }
                for user_profile in user_profiles
            ]).on_conflict_do_nothing().gino.all()

            game_session = await GameSessionModel.create(
                chat_id=chat_id,
                started_at=datetime.utcnow()   # TODO: подружить freezegun с offset-aware datetime
            )
            
            await PlayerSessionModel.insert().gino.all([
                {
                    "vk_id": user_profile.id,
                    "session_id": game_session.id,
                }
                for user_profile in user_profiles
            ])

            return GameSession.from_gino_model(game_session)
        
    async def get_all_player_sessions(self, session_id: int) -> List[PlayerSession]:
        return PlayerSession(0, 0, None)

    async def get_player_session(self, session_id: int, vk_id: int) -> Optional[PlayerSession]:
        return PlayerSession(0, 0, None)
