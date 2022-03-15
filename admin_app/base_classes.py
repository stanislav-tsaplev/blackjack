from typing import Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)

from common.config import Config
from common.db import Database
from admin_app.store import AdminStore
from admin_app.auth.models import Admin


class AdminApplication(AiohttpApplication):
    config: Optional[Config] = None
    database: Optional[Database] = None
    
    db_store: Optional[AdminStore] = None


class Request(AiohttpRequest):
    admin: Optional[Admin] = None

    @property
    def app(self) -> AdminApplication:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request
    
    @property
    def store(self) -> AdminStore:
        return self.request.app.db_store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})
        