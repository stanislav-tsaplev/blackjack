from enum import IntEnum
from operator import attrgetter

from common.db.gino_instance import gino_instance as db


class GameSessionState(IntEnum):
    OPENED = 0
    BETTING = 1
    INITIAL_DEAL = 2
    DEALING = 3
    DEALER_GAME = 4
    PAYING_OUT = 5
    CLOSED = 6
    TERMINATED = 7


class GameSession(db.Model):
    __tablename__ = "game_sessions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id= db.Column(db.Integer,
                db.ForeignKey("game_chats.chat_id", ondelete="CASCADE"))
                
    started_at = db.Column(db.DateTime())
    closed_at = db.Column(db.DateTime(), nullable=True)
    state = db.Column(db.Enum(GameSessionState), 
        nullable=False, default=GameSessionState.OPENED.value
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._player_sessions = list()
        self._game_chat = None

    @property
    def dealer_session(self):
        # assuming dealer's timestamp always remains equal initial value (0)
        return min(self._player_sessions, key=attrgetter("timestamp"))

    @property
    def player_sessions(self):
        """Returns list of player sessions, ordered by timestamp, excluding dealer
        """
        # assuming dealer's timestamp always remains equal initial value (0)
        return sorted(self._player_sessions, key=attrgetter("timestamp"))[1:]

    @player_sessions.setter
    def add_player_session(self, player_session):
        self._player_sessions.append(player_session)
