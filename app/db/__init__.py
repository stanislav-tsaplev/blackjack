import typing

from app.db.core.core import DB

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.db.admin.accessor import AdminAccessor
from app.db.bot.accessors import (
    UserAccessor,
    PlayerAccessor,
    GameChatAccessor,
    GameSessionAccessor,
    PlayerSessionAccessor,
)


def setup_db(app: "Application"):
    app.db = DB(app)
    app.on_startup.append(app.db.connect)
    app.on_cleanup.append(app.db.disconnect)

    app.admins = AdminAccessor(app)
    
    app.users = UserAccessor(app)
    app.players = PlayerAccessor(app)
    app.game_chats = GameChatAccessor(app)
    app.game_sessions = GameSessionAccessor(app)
    app.player_sessions = PlayerSessionAccessor(app)