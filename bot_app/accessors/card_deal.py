from typing import Tuple

from sqlalchemy.dialects.postgresql import insert

from common.db.gino_instance import gino_instance as db
from common.db.gino_models import PlayerSession, PlayerSessionState, CardDeal
from common.base.accessor import BaseAccessor
from bot_app.utils.playcards import Card
from bot_app.utils.player_hand import PlayerHand


class CardDealAccessor(BaseAccessor):
    async def connect(self, app: "BotApplication"):
        await super().connect(app)

    async def add_initial_cards(self, 
        player_session: PlayerSession, 
        cards: Tuple[Card]
    ) -> None:
        async with self.app.database.orm.transaction() as tx:
            await CardDeal.insert().gino.all([
                {
                    "player_session_id": player_session.id,
                    "card_rank": card.rank,
                    "card_suit": card.suit,
                } 
                for card in cards
            ])

            await player_session.update(
                state=PlayerSessionState.DEALING,
            ).apply()

    async def add_card(self, 
        player_session: PlayerSession, 
        card: Card
    ) -> None:
        await insert(CardDeal).values(
            player_session_id=player_session.id,
            card_rank=card.rank,
            card_suit=card.suit,
        ).gino.status()

    async def get_player_hand(self, player_session: PlayerSession) -> PlayerHand:
        player_cards = await db.select([CardDeal]).where(
            CardDeal.player_session_id == player_session.id
        ).gino.load(
            lambda row, ctx: Card(rank=row[2], suit=row[3])
        ).all()

        return PlayerHand(player_cards)