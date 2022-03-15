from logging import getLogger

from aiohttp.web import Application as AiohttpApplication


class BaseAccessor:
    def __init__(self, app: AiohttpApplication, *args, **kwargs):
        self.app = app
        self.logger = getLogger(self.__class__.__name__)
        
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: AiohttpApplication):
        self.logger.info("connect")

    async def disconnect(self, app: AiohttpApplication):
        self.logger.info("disconnect")
