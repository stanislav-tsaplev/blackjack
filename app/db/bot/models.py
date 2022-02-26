from dataclasses import dataclass
from typing import Optional

from app.db.core.gino import db


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
            id=session["player_session"]["vk_id"], 
            email=session["player_session"]["chat_id"]
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