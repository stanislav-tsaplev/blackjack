from typing import TYPE_CHECKING

from admin_app.game_info.views import (
    GameInfoSummaryView
)

if TYPE_CHECKING:
    from admin_app import AdminApplication


def setup_routes(app: "AdminApplication"):
    app.router.add_view("/admin.info.summary", GameInfoSummaryView)