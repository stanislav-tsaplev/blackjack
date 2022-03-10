from typing import Optional, List

from sqlalchemy.dialects.postgresql import insert

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *


class PlayerAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def get_player(self, user_id: int, chat_id: int) -> Optional[Player]:
        return await Player.load(
            user_profile=UserProfile
        ).where(
            db.and_(
                Player.vk_id == user_id,
                Player.chat_id == chat_id
            )
        ).gino.one_or_none()

