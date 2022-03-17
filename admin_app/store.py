from typing import TYPE_CHECKING
from dataclasses import dataclass

from admin_app.auth.accessors.admin import *
from admin_app.games.accessor import GamesAccessor

if TYPE_CHECKING:
    from admin_app import AdminApplication


@dataclass
class AdminStore:
    admins: AdminAccessor
    games: GamesAccessor


def setup_admin_store(app: "AdminApplication"):
    app.db_store = AdminStore(
        admins=AdminAccessor(app),
        games=GamesAccessor(app),
    )
