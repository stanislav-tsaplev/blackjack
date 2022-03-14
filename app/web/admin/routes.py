from typing import TYPE_CHECKING

from app.web.admin.views.login import (
    AdminIndexView,
    AdminLoginView, 
    AdminCurrentView,
)
# from app.web.admin.views.games import AdminInfoGamesView

if TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/admin", AdminIndexView)
    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)
    # app.router.add_view("/admin.info.games", AdminInfoGamesView)