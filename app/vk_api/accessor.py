import random
from typing import List, Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.db.base.accessor import BaseAccessor
from app.vk_api.models import (
    VkApiUpdate,
    VkApiMembersResponse,
    VkApiMemberProfile,
)
from app.bot.poller import Poller
from app.vk_api.utils import build_query_url

import typing
if typing.TYPE_CHECKING:
    from app.web.app import Application


VK_API_PATH = "https://api.vk.com/method/"

class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.poller: Optional[Poller] = None

        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
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

    async def disconnect(self, app: "Application"):
        self.logger.info("disconnect")

        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()   

    async def _get_long_poll_server(self):
        query_url = build_query_url(
            api_path=VK_API_PATH,
            api_method="groups.getLongPollServer",
            params={
                "group_id": self.app.config.bot.group_id,
                "access_token": self.app.config.bot.token,
                "lp_version": 3,
            },
        )
        async with self.session.get(query_url) as response:
            if response.status == 200:
                json = await response.json()
                data = json["response"]
                self.logger.info(data)

                return data["key"], data["server"], data["ts"]
            else:
                self.logger.error(f"error during getting long poll server: {response}")

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
        async with self.session.get(query_url) as response:
            json = await response.json()
            self.logger.info(json)

            if not "failed" in json:
                self.ts = json["ts"]

                try:
                    json_updates = json.get("updates", [])
                    return [VkApiUpdate.from_dict(json_update)
                                for json_update in json_updates]
                except Exception as e:
                    self.logger.error("exception during update parsing", exc_info=e)
            else:
                # "{"failed":1,"ts":$new_ts}— история событий устарела или была частично утеряна, 
                #  приложение может получать события далее, 
                #  используя новое значение ts из ответа.

                # {"failed":2} — истекло время действия ключа, 
                #  нужно заново получить key методом messages.getLongPollServer.

                # {"failed":3} — информация о пользователе утрачена, 
                #  нужно запросить новые key и ts методом messages.getLongPollServer.

                # TODO: implement handling for the failures above
                self.logger.error("error during getting updates")

    async def send_message(self, peer_id: int, text: str) -> None:
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
        async with self.session.get(query_url) as response:
            json = await response.json()
            self.logger.info(json)

            if not "error" in json:
                sent_message_id = int(json["response"])
                self.logger.info(f"message sent with id: {sent_message_id}")
            else:
                self.logger.error("error during message sending")

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
        async with self.session.get(query_url) as response:
            json = await response.json()

            if not "error" in json:
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