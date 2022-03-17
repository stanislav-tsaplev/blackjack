from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

from common.db.gino_instance import gino_instance as db
from common.db.gino_models import *


@dataclass
class PlayerInfo:
    vk_id: int
    first_name: str
    last_name: str
    city: str
    bet: int
    gain: int

    @classmethod
    def from_gino_model(cls, player_session: PlayerSession) -> "PlayerInfo":            
        return cls(
            vk_id=player_session.player.vk_id,
            first_name=player_session.player.user_profile.first_name,
            last_name=player_session.player.user_profile.last_name,
            city=player_session.player.user_profile.city,
            bet=player_session.bet,
            gain=(
                player_session.bet and player_session.payout_ratio 
                and player_session.bet * player_session.payout_ratio
            ),
        )


@dataclass
class GameInfo:
    chat_id: int
    chat_name: str
    started_at: datetime
    closed_at: datetime
    players: List[PlayerInfo]

    @classmethod
    def from_gino_model(cls, game_session: GameSession) -> "GameInfo":            
        return cls(
            chat_id=game_session.chat_id, 
            chat_name=game_session.game_chat.name,
            started_at=game_session.started_at,
            closed_at=game_session.closed_at,
            players=[
                PlayerInfo.from_gino_model(player_session)
                for player_session in game_session.player_sessions
            ]
        )

@dataclass
class GamesSummary:
    total: int
    games: List[GameInfo]

    @classmethod
    def from_gino_model(cls, game_sessions: List[GameSession]) -> "GamesSummary":            
        return cls(
            total=len(game_sessions),
            games=[
                GameInfo.from_gino_model(game_session) 
                for game_session in game_sessions
            ]
        )
