from enum import IntEnum

from common.db.gino_instance import gino_instance as db


class CardRank(IntEnum):
    Ace = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13


class CardSuit(IntEnum):
    Clubs = 1
    Diamonds = 2
    Hearts = 3
    Spades = 4


class CardDeal(db.Model):
    __tablename__ = "card_deals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_session_id = db.Column(db.Integer, 
        db.ForeignKey("player_sessions.id", ondelete="CASCADE"))
    card_rank = db.Column(db.Enum(CardRank), nullable=False)
    card_suit = db.Column(db.Enum(CardSuit), nullable=False)