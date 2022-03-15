import random
from typing import List, Optional, TYPE_CHECKING

from aiohttp import ClientConnectionError, TCPConnector
from aiohttp.client import ClientSession

from common.base.accessor import BaseAccessor
from bot_app.vk_api.models import (
    VkApiUpdate,
    VkApiMembersResponse,
    VkApiMemberProfile,
)
from bot_app.core.poller import Poller
from bot_app.vk_api.utils import build_query_url

if TYPE_CHECKING:
    from bot_app import BotApplication


VK_API_PATH = "https://api.vk.com/method/"

class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "BotApplication", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.poller: Optional[Poller] = None

        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "BotApplication"):
        self.logger.info("connect")

        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            self.key, self.server, self.ts = await self._get_long_poll_server()
        except Exception as e:
            self.logger.error("exception during long poll service getting", exc_info=e)
            await self.session.close()

        self.logger.info("start polling")
        self.poller = Poller(app)
        await self.poller.start()

    async def disconnect(self, app: "BotApplication"):
        self.logger.info("disconnect")

        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()  

    async def _get_long_poll_server(self) -> None:
        query_url = build_query_url(
            api_path=VK_API_PATH,
            api_method="groups.getLongPollServer",
            params={
                "group_id": self.app.config.bot.group_id,
                "access_token": self.app.config.bot.token,
                "lp_version": 3,
            },
        )
        try:
            async with self.session.get(query_url) as response:
                if response.status != 200:
                    error_message = f"error during getting long poll server: {response}"
                    self.logger.error(error_message)
                    raise ConnectionError(error_message)
                
                json = await response.json()
                data = json["response"]
                self.logger.info(data)

                return data["key"], data["server"], data["ts"]
        except ClientConnectionError as e:
            self.logger.error("connection error during getting long poll server", exc_info=e)
            self.session.close()
            self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
            await self._get_long_poll_server()


    async def poll(self) -> list[VkApiUpdate]:
        query_url = build_query_url(
            api_path=self.server,
            api_method="",
            params={
                "act": "a_check",
                "key": self.key,
                "ts": self.ts,
                "wait": 25,     # recommended value
                "mode": 2,
                "version": 3,
            },
        )
        try:
            async with self.session.get(query_url) as response:
                json = await response.json()
                self.logger.info(json)

                if "failed" not in json:
                    self.ts = json["ts"]
                    try:
                        json_updates = json.get("updates", [])
                        return [
                            VkApiUpdate.from_dict(json_update)
                            for json_update in json_updates
                        ]
                    except Exception as e:
                        self.logger.error("exception during update parsing", exc_info=e)
                else:
                    self.logger.error("error during getting updates")
                    error_code = int(json["failed"])
                    
                    # "{"failed":1,"ts":$new_ts} — 
                    # история событий устарела или была частично утеряна, 
                    # приложение может получать события далее, 
                    # используя новое значение ts из ответа.
                    if error_code == 1:
                        self.ts = json["ts"]

                    # {"failed":2} — истекло время действия ключа, 
                    #  нужно заново получить key методом messages.getLongPollServer.
                    # {"failed":3} — информация о пользователе утрачена, 
                    #  нужно запросить новые key и ts методом messages.getLongPollServer.
                    elif error_code in (2, 3):
                        try:
                            self.key, self.server, self.ts = await self._get_long_poll_server()
                        except Exception as e:
                            self.logger.error(
                                "exception during long poll service getting", 
                                exc_info=e
                            )
                            await self.session.close()
                                                
                    return await self.poll()
        
        except ClientConnectionError as e:
            self.logger.error("connection error during getting updates", exc_info=e)
            self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
            return await self.poll()

    async def send_message(self, peer_id: int, text: str) -> int:
        query_url = build_query_url(
            api_path=VK_API_PATH,
            api_method="messages.send",
            params={
                "random_id": random.randint(1, 2**32),
                "peer_id": peer_id,
                "message": text,
                "access_token": self.app.config.bot.token,
            },
        )
        try:
            async with self.session.get(query_url) as response:
                json = await response.json()
                self.logger.info(json)

                if "error" not in json:
                    sent_message_id = int(json["response"])
                    self.logger.info(f"message sent with id: {sent_message_id}")
                    return sent_message_id
                else:
                    self.logger.error("error during message sending")
                    return None
        except ClientConnectionError as e:
            self.logger.error(exc_info=e)
            self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
            await self.send_message(peer_id, text)

    async def send_message_with_keyboard(self, peer_id: int, text: str, keyboard: str) -> int:
        query_url = build_query_url(
            api_path=VK_API_PATH,
            api_method="messages.send",
            params={
                "random_id": random.randint(1, 2**32),
                "peer_id": peer_id,
                "message": text,
                "keyboard": keyboard,
                "access_token": self.app.config.bot.token,
            },
        )
        try:
            async with self.session.get(query_url) as response:
                json = await response.json()
                self.logger.info(json)

                if "error" not in json:
                    sent_message_id = int(json["response"])
                    self.logger.info(f"message sent with id: {sent_message_id}")
                    return sent_message_id
                else:
                    self.logger.error("error during message sending")
                return None
        except ClientConnectionError as e:
            self.logger.error(exc_info=e)
            self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
            await self.send_message_with_keyboard(peer_id, text, keyboard)

    async def update_message(self, peer_id: int, message_id: int, text: str) -> None:
        query_url = build_query_url(
            api_path=VK_API_PATH,
            api_method="messages.edit",
            params={
                "peer_id": peer_id,
                "message_id": message_id,
                "message": text,
                "access_token": self.app.config.bot.token,
            },
        )
        try:
            async with self.session.get(query_url) as response:
                json = await response.json()
                self.logger.info(json)

                if "error" not in json:
                    self.logger.info(f"message with id: {message_id} updated")
                else:
                    self.logger.error("error during message sending")
        except ClientConnectionError as e:
            self.logger.error(exc_info=e)
            self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
            await self.update_message(peer_id, message_id, text)


    async def get_active_member_profiles(self, peer_id: int
    ) -> List[VkApiMemberProfile]:
        query_url = build_query_url(
            api_path=VK_API_PATH,
            api_method="messages.getConversationMembers",
            params={
                "peer_id": peer_id,
                "fields": "online",
                "access_token": self.app.config.bot.token,
            },
        )
        try:
            async with self.session.get(query_url) as response:
                json = await response.json()

                if "error" not in json:
                    chat_members_info = VkApiMembersResponse.from_dict(json["response"])
                    active_chat_member_profiles = [
                        profile for profile 
                        in chat_members_info.profiles 
                        if profile.online
                    ]

                    self.logger.info(f"active members in chat {peer_id}: {active_chat_member_profiles}")
                    return active_chat_member_profiles
                else:
                    self.logger.error(f"error during getting chat members: {json}")
        except ClientConnectionError as e:
            self.logger.error(exc_info=e)
            self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
            return await self.get_active_member_profiles(peer_id)