import typing

from app.db.core.core import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.db.admin.accessor import AdminAccessor
from app.db.game.accessors import *


@dataclass
class Storage:
    admins: AdminAccessor
    
    users: UserAccessor
    players: PlayerAccessor
    game_chats: GameChatAccessor
    game_sessions: GameSessionAccessor
    player_sessions: PlayerSessionAccessor
    

def setup_db(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)

    app.storage = Storage(
        admins = AdminAccessor(app),
    
        users = UserAccessor(app),
        players = PlayerAccessor(app),
        game_chats = GameChatAccessor(app),
        game_sessions = GameSessionAccessor(app),
        player_sessions = PlayerSessionAccessor(app),
    )