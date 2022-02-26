import typing
from logging import getLogger

from app.vk_api.models import (
    Update, Message
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None

        self.logger = getLogger(self.__class__.__name__)

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == "message_new":
                message_to_send = Message(
                    user_id=update.object.user_id, 
                    text=f"Message received: {update.object.body}"
                )
                await self.app.store.vk_api.send_message(message_to_send)
