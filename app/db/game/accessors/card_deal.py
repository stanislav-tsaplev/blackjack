from typing import Tuple

from sqlalchemy.dialects.postgresql import insert

from app.db.core.gino import gino_orm as db
from app.db.base.accessor import BaseAccessor
from app.db.game.models import PlayerSession, CardDeal
from app.bot.utils.playcards import Card
from app.bot.utils.scores import PlayerHand


class CardDealAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

    async def add_cards(self, 
                        player_session: PlayerSession, 
                        cards: Tuple[Card]) -> None:
        await CardDeal.insert().gino.all([
            {
                "player_session_id": player_session.id,
                "card_rank": card.rank,
                "card_suit": card.suit,
            } 
            for card in cards
        ])

    async def get_player_hand(self, player_session: PlayerSession) -> PlayerHand:
        player_cards = await db.select([CardDeal]).where(
            CardDeal.player_session_id == player_session.id
        ).gino.load(
            lambda row, ctx: Card(rank=row[2], suit=row[3])
        ).all()

        return PlayerHand(player_cards)