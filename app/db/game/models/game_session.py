from enum import IntEnum

from app.db.core.gino import gino_orm as db


class GameSessionState(IntEnum):
    OPENED = 0
    CLOSED = 1
    TERMINATED = 2


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

    @property
    def player_sessions(self):
        return self._player_sessions

    @player_sessions.setter
    def add_player_session(self, player_session):
        self._player_sessions.append(player_session)
