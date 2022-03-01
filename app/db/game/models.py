from dataclasses import dataclass
from enum import IntEnum
from datetime import datetime
from typing import Optional

from app.db.core.gino import gino_orm as db


@dataclass
class Player:
    vk_id: int
    chat_id: int
    money: int
    
    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Player"]:
        if session is None:
            return None

        return cls(
            vk_id=session["player"]["vk_id"], 
            chat_id=session["player"]["chat_id"],
            money=session["player"]["money"]
        )

    @classmethod
    def from_gino_model(cls, model: Optional["PlayerModel"]) -> Optional["Player"]:
        if model is None:
            return None
            
        return cls(
            vk_id=model.vk_id,
            chat_id=model.chat_id, 
            money=model.money
        )


class PlayerModel(db.Model):
    __tablename__ = "players"

    vk_id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.Integer(), primary_key=True)
    money = db.Column(db.Integer(), default=0)


class GameSessionState(IntEnum):
    OPENED = 0
    CLOSED = 1
    TERMINATED = 2


@dataclass
class GameSession:
    id: int
    chat_id: int
    started_at: datetime
    closed_at: Optional[datetime]
    state: GameSessionState
    
    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["GameSession"]:
        if session is None:
            return None

        return cls(
            id=session["game_session"]["id"], 
            chat_id=session["player_session"]["chat_id"],
            started_at=session["player_session"]["started_at"],
            closed_at=session["player_session"]["closed_at"],
            state=session["player_session"]["state"]
        )

    @classmethod
    def from_gino_model(cls, model: Optional["GameSessionModel"]) -> Optional["GameSession"]:
        if model is None:
            return None
            
        return cls(
            id=model.id,
            chat_id=model.chat_id,
            started_at=model.started_at,
            closed_at=model.closed_at,
            state=model.state,
        )


class GameSessionModel(db.Model):
    __tablename__ = "game_sessions"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    chat_id= db.Column(db.Integer())
    started_at = db.Column(db.DateTime())
    closed_at = db.Column(db.DateTime(), nullable=True)
    state = db.Column(db.Enum(GameSessionState), default=GameSessionState.OPENED.value)


@dataclass
class PlayerSession:
    vk_id: int
    session_id: int
    gain: Optional[int]
    
    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["PlayerSession"]:
        if session is None:
            return None

        return cls(
            vk_id=session["player_session"]["vk_id"], 
            session_id=session["player_session"]["session_id"],
            gain=session["player_session"]["gain"]
        )

    @classmethod
    def from_gino_model(cls, model: Optional["PlayerSessionModel"]) -> Optional["PlayerSession"]:
        if model is None:
            return None
            
        return cls(
            vk_id=model.vk_id,
            session_id=model.session_id, 
            gain=model.gain
        )


class PlayerSessionModel(db.Model):
    __tablename__ = "player_sessions"

    vk_id = db.Column(db.Integer(), primary_key=True)
    session_id = db.Column(db.Integer(), primary_key=True)
    gain = db.Column(db.Integer(), nullable=True)