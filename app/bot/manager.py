from typing import Optional
from logging import getLogger

from app.vk_api.models import VkApiUpdate
from app.bot.resources import VK_MESSAGES

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None

        self.logger = getLogger(self.__class__.__name__)

        self.command_handlers = {
            "start.game": self.start_game
        }

    @staticmethod
    def _try_get_command(text: str) -> Optional[str]:
        if text and text[0] == '/':
            return text[1:]
        else:
            return None

    async def start_game(self, user_id: int, chat_id: int):
        current_game_session = await self.app.storage.games.get_current_game_session(chat_id)
        if current_game_session is None:
            active_member_profiles = await self.app.vk_api \
                                        .get_active_member_profiles(chat_id)            
            created_game_session = await self.app.storage.games \
                                        .create_game_session(
                                            chat_id, 
                                            active_member_profiles
                                        )
            
            await self.app.vk_api.send_message(
                chat_id, 
                f'{VK_MESSAGES["game.start"]}. {VK_MESSAGES["game.players_list_header"]}'
            )
            for index, profile in enumerate(active_member_profiles, start=1):
                await self.app.vk_api.send_message(
                    chat_id, 
                    f"{index}) {profile.first_name} {profile.last_name}"
                )
        else:
            await self.app.vk_api.send_message(chat_id, VK_MESSAGES["game.already_started"])

    async def handle_updates(self, updates: list[VkApiUpdate]):
        for update in updates:
            if update.type == "message_new":
                vk_api_message = update.object.message

                command = self._try_get_command(vk_api_message.text)
                if command is None:
                    continue    
                elif command == "game.start":
                    await self.start_game(
                        user_id=vk_api_message.from_id,
                        chat_id=vk_api_message.peer_id,
                    )
