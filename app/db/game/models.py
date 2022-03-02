from dataclasses import dataclass
from enum import IntEnum
from datetime import datetime
from typing import Optional

from app.db.core.gino import gino_orm as db


@dataclass
class User:
    vk_id: int
    first_name: str
    last_name: str
    city: Optional[str]

    @classmethod
    def from_gino_model(cls, model: Optional["UserModel"]) -> Optional["User"]:
        if model is None:
            return None
            
        return cls(
            vk_id=model.vk_id,
            first_name=model.first_name,
            last_name=model.last_name,
            city=model.city
        )


class UserModel(db.Model):
    __tablename__ = "users"

    vk_id = db.Column(db.Integer(), unique=True, primary_key=True)
    first_name = db.Column(db.Unicode())
    last_name = db.Column(db.Unicode())
    city = db.Column(db.Unicode(), nullable=True)

###############

@dataclass
class GameChat:
    chat_id: int
    name: Optional[str]

    @classmethod
    def from_gino_model(cls, model: Optional["GameChatModel"]) -> Optional["GameChat"]:
        if model is None:
            return None
            
        return cls(
            chat_id=model.chat_id, 
            name=model.name
        )


class GameChatModel(db.Model):
    __tablename__ = "game_chats"

    chat_id = db.Column(db.Integer(), unique=True, primary_key=True)
    name = db.Column(db.Unicode(), nullable=True)

###############

@dataclass
class Player:
    vk_id: int
    chat_id: int
    money: int

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

    vk_id = db.Column(db.Integer(), 
        db.ForeignKey("users.vk_id", ondelete="CASCADE"),
        primary_key=True
    )
    chat_id = db.Column(db.Integer(),
        db.ForeignKey("game_chats.chat_id", ondelete="CASCADE"),
        primary_key=True
    )
    money = db.Column(db.Integer(), default=0)
    
###############

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
    def from_gino_model(cls, 
        model: Optional["GameSessionModel"]
    ) -> Optional["GameSession"]:
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
    chat_id= db.Column(db.Integer(),
        db.ForeignKey("game_chats.chat_id", ondelete="CASCADE")
    )
    started_at = db.Column(db.DateTime())
    closed_at = db.Column(db.DateTime(), nullable=True)
    state = db.Column(db.Enum(GameSessionState), 
        nullable=False, default=GameSessionState.OPENED.value
    )

###############

class PlayerSessionState(IntEnum):
    WAITING = 0
    HITTING = 1
    STANDING = 2
    BUSTED = 3
    PAID_OUT = 4


@dataclass
class PlayerSession:
    vk_id: int
    session_id: int
    bet: Optional[int]
    payout_ratio: Optional[int]
    state: PlayerSessionState

    @classmethod
    def from_gino_model(cls, 
        model: Optional["PlayerSessionModel"]
    ) -> Optional["PlayerSession"]:
        if model is None:
            return None
            
        return cls(
            vk_id=model.vk_id,
            session_id=model.session_id, 
            bet=model.bet,
            payout_ratio=model.payout_ratio,
            state=model.state
        )


class PlayerSessionModel(db.Model):
    __tablename__ = "player_sessions"

    vk_id = db.Column(db.Integer(), primary_key=True)
    session_id = db.Column(db.Integer(), 
        db.ForeignKey("game_sessions.id", ondelete="CASCADE"),
        primary_key=True
    )
    bet = db.Column(db.Integer(), nullable=True)
    payout_ratio = db.Column(db.Integer(), nullable=True)
    state = db.Column(db.Enum(PlayerSessionState), 
        nullable=False, default=PlayerSessionState.WAITING.value
    )

###############

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


@dataclass
class CardDeal:
    session_id: int
    vk_id: int
    timestamp: int
    card_rank: CardRank
    card_suit: CardSuit

    @classmethod
    def from_gino_model(cls, model: Optional["CardDealModel"]) -> Optional["CardDeal"]:
        if model is None:
            return None
            
        return cls(
            session_id=model.session_id,
            vk_id=model.vk_id,
            timestamp=model.timestamp,
            card_rank=model.card_rank,
            card_suit=model.card_suit
        )


class CardDealModel(db.Model):
    __tablename__ = "card_deals"

    session_id = db.Column(db.Integer(), 
        db.ForeignKey("game_sessions.id", ondelete="CASCADE"),    
        primary_key=True
    )
    vk_id = db.Column(db.Integer(), primary_key=True)
    timestamp = db.Column(db.Integer(), primary_key=True)
    card_rank = db.Column(db.Enum(CardRank), nullable=False)
    card_suit = db.Column(db.Enum(CardSuit), nullable=False)
