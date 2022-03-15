from typing import Optional

from aiohttp.web import Application as AiohttpApplication

from common.config import Config
from common.db import Database
from bot_app.vk_api import VkApiAccessor
from bot_app.store import BotStore
from bot_app.core import BotManager


class BotApplication(AiohttpApplication):
    config: Optional[Config] = None
    database: Optional[Database] = None
    
    db_store: Optional[BotStore] = None
    vk_api: Optional[VkApiAccessor] = None
    bot: Optional[BotManager] = None

