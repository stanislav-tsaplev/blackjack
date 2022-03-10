from typing import TYPE_CHECKING
from logging import getLogger

if TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)
        
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        self.logger.info("connect")

    async def disconnect(self, app: "Application"):
        self.logger.info("disconnect")
