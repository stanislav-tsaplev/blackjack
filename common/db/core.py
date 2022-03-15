from typing import Optional
import logging
import os


from aiohttp.web import Application as AiohttpApplication
from sqlalchemy.engine.url import URL
from gino import create_engine

from common.db.gino_instance import Gino, gino_instance


class Database:
    # orm: Optional[Gino]

    def __init__(self, app: AiohttpApplication):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.app = app
        self.orm: Optional[Gino] = None


    async def connect(self, *args, **kwargs):
        self.logger.info('connect')
        
        # self._engine = await create_engine(
        #     URL(
        #         drivername="asyncpg",
        #         host=self.app.config.db.host,
        #         port=self.app.config.db.port,
        #         database=self.app.config.db.dbname,
        #         username=self.app.config.db.user,
        #         password=self.app.config.db.password,
        #     ),
        #     min_size=1,
        #     max_size=1,
        # )
        self._engine = await create_engine(
            os.environ["DATABASE_URL"]
        )
        self.orm = gino_instance
        self.orm.bind = self._engine
        

    async def disconnect(self, *args, **kwargs):
        self.logger.info('disconnect')
        if self.orm:
            await self.orm.pop_bind().close()
            self.orm = None
            self._engine = None
