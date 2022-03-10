from typing import TYPE_CHECKING

from app.web.admin.views import (
    AdminLoginView, 
    AdminCurrentView
)

if TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)
