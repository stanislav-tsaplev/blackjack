from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from bot_app import BotApplication

from bot_app.accessors import *


@dataclass
class BotStore:
    players: PlayerAccessor
    game_sessions: GameSessionAccessor
    player_sessions: PlayerSessionAccessor
    player_dataports: PlayerDataportAccessor
    card_deals: CardDealAccessor


def setup_bot_store(app: "BotApplication"):
    app.db_store = BotStore(
        players=PlayerAccessor(app),
        game_sessions=GameSessionAccessor(app),
        player_sessions=PlayerSessionAccessor(app),
        player_dataports=PlayerDataportAccessor(app),
        card_deals=CardDealAccessor(app),
    )
