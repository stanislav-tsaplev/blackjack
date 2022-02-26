from logging import getLogger
import gino
from gino.api import Gino
from sqlalchemy.engine.url import URL

from app.db.core.gino import db
from app.db.admin.models import *
from app.db.bot.models import *


class DB:
    db: Optional[Gino]

    def __init__(self, app: "Application"):
        self.app = app
        self.db: Optional[Gino] = None

        self.logger = getLogger(self.__class__.__name__)

    async def connect(self, *args, **kwargs):
        self.logger.info('connect')
        
        self._engine = await gino.create_engine(
            URL(
                drivername="asyncpg",
                host=self.app.config.db.host,
                port=self.app.config.db.port,
                database=self.app.config.db.dbname,
                username=self.app.config.db.user,
                password=self.app.config.db.password,
            ),
            min_size=1,
            max_size=1,
        )
        self.db = db
        self.db.bind = self._engine
        

    async def disconnect(self, *args, **kwargs):
        self.logger.info('disconnect')
        if self.db:
            await self.db.pop_bind().close()
            self.db = None
            self._engine = None
