import typing

from app.db.core.core import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.db.admin.accessor import AdminAccessor
from app.db.game.accessor import *


@dataclass
class Storage:
    admins: AdminAccessor
    games: GameAccessor
    

def setup_db(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)

    app.storage = Storage(
        admins = AdminAccessor(app),
        games = GameAccessor(app)
    )