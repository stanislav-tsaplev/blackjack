from typing import TYPE_CHECKING
from dataclasses import dataclass

from app.db.core.core import Database

if TYPE_CHECKING:
    from app.web.app import Application

from app.db.admin.accessor import AdminAccessor
from app.db.game.accessors import *


@dataclass
class Store:
    admins: AdminAccessor
    players: PlayerAccessor
    game_sessions: GameSessionAccessor
    player_sessions: PlayerSessionAccessor
    player_dataports: PlayerDataportAccessor
    card_deals: CardDealAccessor
    

def setup_database(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)

    app.db_store = Store(
        admins=AdminAccessor(app),
        players=PlayerAccessor(app),
        game_sessions=GameSessionAccessor(app),
        player_sessions=PlayerSessionAccessor(app),
        player_dataports=PlayerDataportAccessor(app),
        card_deals=CardDealAccessor(app),
    )