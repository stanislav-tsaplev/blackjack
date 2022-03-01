from sqlalchemy.engine.url import URL
import gino
from gino.api import Gino
from logging import getLogger

from app.db.core.gino import gino_orm
from app.db.admin.models import *
from app.db.game.models import *


class Database:
    orm: Optional[Gino]

    def __init__(self, app: "Application"):
        self.app = app
        self.orm: Optional[Gino] = None

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
        self.orm = gino_orm
        self.orm.bind = self._engine
        

    async def disconnect(self, *args, **kwargs):
        self.logger.info('disconnect')
        if self.orm:
            await self.orm.pop_bind().close()
            self.orm = None
            self._engine = None
