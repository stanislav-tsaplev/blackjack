from typing import Optional, List

from common.base.accessor import BaseAccessor
from bot_app.game.models import *


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
        max_size: int = 0, offset: int = 0    
    ) -> List[Player]:
        query = Player.load(
            user_profile=UserProfile,
            game_chat=GameChat.distinct(GameChat.chat_id)
        ).query.where(
            UserProfile.vk_id != self.app.config.bot.group_id
        ).order_by(
            Player.money.desc()
        )

        if max_size > 0:
            return await query.limit(max_size).offset(0).gino.all()
        else:
            return await query.offset(0).gino.all()