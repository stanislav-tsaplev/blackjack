from typing import TYPE_CHECKING
from dataclasses import dataclass

from admin_app.auth.accessors.admin import *
from admin_app.game_info.accessors.summary import *

if TYPE_CHECKING:
    from admin_app import AdminApplication


@dataclass
class AdminStore:
    admins: AdminAccessor
    game_info: GameInfoAccessor


def setup_admin_store(app: "AdminApplication"):
    app.db_store = AdminStore(
        admins=AdminAccessor(app),
        game_info=GameInfoAccessor(app),
    )
