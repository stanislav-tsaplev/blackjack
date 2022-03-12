from enum import IntEnum

from app.db.core.gino import gino_orm as db


class PlayerSessionState(IntEnum):
    BETTING = 0
    INITIAL_DEAL = 1
    DEALING = 2
    STANDING = 3
    BLACKJACKED = 4
    BUSTED = 5
    PAIDOUT = 6
    CUTOUT = 7


class PlayerSession(db.Model):
    __tablename__ = "player_sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_session_id = db.Column(db.Integer, 
        db.ForeignKey("game_sessions.id", ondelete="CASCADE"))
    player_id = db.Column(db.Integer,
        db.ForeignKey("players.id", ondelete="CASCADE"))
    timestamp = db.Column(db.BigInteger, default=0)

    bet = db.Column(db.Integer, nullable=True)
    payout_ratio = db.Column(db.Integer, nullable=True)
    state = db.Column(db.Enum(PlayerSessionState), 
        nullable=False, default=PlayerSessionState.BETTING.value)

    secondary_key = db.Index("player_sessions.skey", 
                                "player_id", "game_session_id", unique=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._card_deals = list()
        self._player_dataport = None

    @property
    def card_deals(self):
        return self._card_deals

    @card_deals.setter
    def add_card_deal(self, card_deal):
        self._card_deals.append(card_deal)

    @property
    def player_dataport(self):
        return self._player_dataport

    @player_dataport.setter
    def add_player_dataport(self, player_dataport):
        self._player_dataport = player_dataport