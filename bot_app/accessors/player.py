from typing import Optional, List

from common.db.gino_models import *
from common.base.accessor import BaseAccessor


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

    async def get_successful_players_list(self, 
        chat_id: int, limit: int = 0, offset: int = 0    
    ) -> List[Player]:
        query = Player.load(
            user_profile=UserProfile
        ).query.where(
            db.and_(
                Player.chat_id == chat_id,
                UserProfile.vk_id != self.app.config.bot.group_id,
            )
        ).order_by(
            Player.money.desc()
        )

        if limit > 0:
            return await query.limit(limit).offset(offset).gino.all()
        else:
            return await query.offset(offset).gino.all()