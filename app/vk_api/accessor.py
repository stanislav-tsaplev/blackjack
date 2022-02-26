import random
import typing
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.db.base.accessor import BaseAccessor
from app.vk_api.models import (
    Update, Message, UpdateObject
)
from app.bot.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


API_PATH = "https://api.vk.com/method/"

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
            self.key, self.server, self.ts = await self._get_long_poll_service()
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

    @staticmethod
    def _build_query(api_path: str, api_method: str, params: dict) -> str:
        params.setdefault("v", "5.131")

        url = f"{api_path}{api_method}?" + \
            "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        query_url = VkApiAccessor._build_query(
            api_path=API_PATH,
            api_method="groups.getLongPollServer",
            params={
                "group_id": self.app.config.bot.group_id,
                "access_token": self.app.config.bot.token,
            },
        )
        async with self.session.get(query_url) as response:
            json = await response.json()
            data = json["response"]
            self.logger.info(data)

            return data["key"], data["server"], data["ts"]

    async def poll(self) -> list[Update]:
        query_url = VkApiAccessor._build_query(
            api_path=self.server,
            api_method="",
            params={
                "act": "a_check",
                "key": self.key,
                "ts": self.ts,
                "wait": 25,     # recommended value
            },
        )
        async with self.session.get(query_url) as response:
            data = await response.json()
            self.logger.info(data)

            self.ts = data["ts"]

            raw_updates = data.get("updates", [])
            return [Update(type=raw_update["type"],
                            object=UpdateObject(
                                id=raw_update["object"]["message"]["id"],
                                user_id=raw_update["object"]["message"]["from_id"],
                                body=raw_update["object"]["message"]["text"],
                            )
                    )
                    for raw_update in raw_updates]

    async def send_message(self, message: Message) -> None:
        query_url = VkApiAccessor._build_query(
            api_path=API_PATH,
            api_method="messages.send",
            params={
                "user_id": message.user_id,
                "random_id": random.randint(1, 2**32),
                "peer_id": f"-{self.app.config.bot.group_id}",
                "message": message.text,
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
                self.logger.info(json)
