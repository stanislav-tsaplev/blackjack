from typing import Optional, TYPE_CHECKING

from common.base.accessor import BaseAccessor
from admin_app.game_info.models.summary import *

if TYPE_CHECKING:
    from admin_app import AdminApplication


class GameInfoAccessor(BaseAccessor):
    async def connect(self, app: "AdminApplication"):
        await super().connect(app)
