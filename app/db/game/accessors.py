from datetime import datetime, timezone
from typing import Optional, List

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *


class UserAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

class PlayerAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

class GameChatAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

class GameSessionAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def get_current_game_session(self, chat_id: int) -> Optional[GameSession]:
        game_session = await GameSessionModel.query \
            .where(
                GameSessionModel.chat_id == chat_id
                and
                GameSessionModel.state == GameSessionState.OPENED
            ).gino.one_or_none()
        return game_session

    async def create_game_session(self, chat_id: int) -> GameSession:
        game_session = await GameSessionModel.create(
            chat_id=chat_id,
            started_at=datetime.now()
        )
        return GameSession.from_gino_model(game_session)

class PlayerSessionAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)
        
    async def get_all_player_sessions(self, session_id: int) -> List[PlayerSession]:
        return PlayerSession(0, 0, None)

    async def get_player_session(self, session_id: int, vk_id: int) -> Optional[PlayerSession]:
        return PlayerSession(0, 0, None)

    async def create_player_sessions(self, session_id: int, vk_ids: List[int]):
        return []
