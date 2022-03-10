from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.db.core.core import Database
from app.db.admin.models import Admin
from app.logger import setup_logging
from app.config import Config, setup_config
from app.web.routes import setup_routes
from app.web.middlewares import setup_middlewares
from app.db import Store, setup_database
from app.vk_api import VkApiAccessor, setup_vk_api
from app.bot import BotManager, setup_bot_manager


class Application(AiohttpApplication):
    config: Optional[Config] = None
    database: Optional[Database] = None
    
    db_store: Optional[Store] = None
    vk_api: Optional[VkApiAccessor] = None
    bot: Optional[BotManager] = None


class Request(AiohttpRequest):
    admin: Optional[Admin] = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)

    setup_routes(app)
    setup_session(app, EncryptedCookieStorage(app.config.session.key))
    setup_aiohttp_apispec(app, title="Vk Blackjack Bot", 
                            url="/docs/json", swagger_path="/docs")
    setup_middlewares(app)
    setup_database(app)
    setup_vk_api(app)
    setup_bot_manager(app)

    return app
