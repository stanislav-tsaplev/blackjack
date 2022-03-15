from typing import TYPE_CHECKING

from admin_app.auth.views.admin import (
    AdminIndexView,
    AdminLoginView,
    AdminCurrentView,
)

if TYPE_CHECKING:
    from admin_app import AdminApplication


def setup_routes(app: "AdminApplication"):
    app.router.add_view("/admin", AdminIndexView)
    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)