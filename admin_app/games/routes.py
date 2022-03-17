from typing import TYPE_CHECKING

from admin_app.games.views import (
    GameSummaryView
)

if TYPE_CHECKING:
    from admin_app import AdminApplication


def setup_routes(app: "AdminApplication"):
    app.router.add_view("/admin.summary", GameSummaryView)