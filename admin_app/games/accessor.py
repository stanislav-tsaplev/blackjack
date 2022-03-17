from typing import Optional, TYPE_CHECKING

from common.base.accessor import BaseAccessor
from common.db.gino_models import (
    GameSessionState,
    GameSession,
    PlayerSession,
    Player,
    UserProfile,
    GameChat,
)
from admin_app.games.models import (
    GamesSummary,
    GameInfo,
    PlayerInfo
)

if TYPE_CHECKING:
    from admin_app import AdminApplication


class GamesAccessor(BaseAccessor):
    async def connect(self, app: "AdminApplication"):
        await super().connect(app)

    async def get_summary(self, 
        offset: Optional[int] = None, limit: Optional[int] = None
    ) -> GamesSummary:
        if offset is None and limit is None:
            game_sessions = await GameSession.distinct(GameSession.id).load(
                add_player_session=PlayerSession.load(
                    player=Player.load(
                        user_profile=UserProfile
                    )
                ),
                game_chat=GameChat,
            ).where(
                GameSession.state == GameSessionState.CLOSED
            ).where(
                Player.id != self.app.config.bot.group_id
            ).gino.all()
            
        else:
            query = GameSession.query.where(
                GameSession.state == GameSessionState.CLOSED
            )

            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            closed_game_sessions = await query.gino.all()
            game_sessions = await GameSession.distinct(GameSession.id).load(
                add_player_session=PlayerSession.load(
                    player=Player.load(
                        user_profile=UserProfile
                    )
                ),
                game_chat=GameChat,
            ).where(
                GameSession.id.in_(gs.id for gs in closed_game_sessions)
            ).where(
                Player.id != self.app.config.bot.group_id
            ).gino.all()
        
        return GamesSummary.from_gino_model(game_sessions)