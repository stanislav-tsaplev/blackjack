from typing import Union
import json

from sqlalchemy.dialects.postgresql import insert

from app.db.base.accessor import BaseAccessor
from app.db.game.models import *


class PlayerDataportAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def put_player_request_data(self, user_id: int, chat_id: int,
                                        request_data: Union[str, list, dict]) -> None:
        player_session = await self.app.db_store \
            .player_sessions.get_current_player_session(user_id, chat_id)

        await player_session.player_dataport.update(
            request_data=json.dumps(request_data)
        ).apply()
        
    async def get_player_request_data(self, user_id: int, chat_id: int,
                                                ) -> Union[str, list, dict, None]:
        player_session = await self.app.db_store \
            .player_sessions.get_current_player_session(user_id, chat_id)

        return json.loads(player_session.player_dataport.request_data)
        
    async def put_player_response_data(self, user_id: int, chat_id: int,
                                        response_data: Union[str, list, dict]) -> None:
        player_session = await self.app.db_store \
            .player_sessions.get_current_player_session(user_id, chat_id)

        await player_session.player_dataport.update(
            response_data=json.dumps(response_data)
        ).apply()
        
    async def get_player_response_data(self, user_id: int, chat_id: int,
                                        ) -> Union[str, list, dict, None]:
        player_session = await self.app.db_store \
            .player_sessions.get_current_player_session(user_id, chat_id)

        response_data = player_session.player_dataport.response_data
        if response_data is None:
            return None            
        return json.loads(response_data)

    async def clear_player_dataport(self, user_id: int, chat_id: int) -> None:
        player_session = await self.app.db_store \
            .player_sessions.get_current_player_session(user_id, chat_id)

        await player_session.player_dataport.update(
            request_data=None, response_data=None
        ).apply()