import typing

from app.web.bot.views import (
    PlayerHitView,
    PlayerStandView,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/player.hit", PlayerHitView)
    app.router.add_view("/player.stand", PlayerStandView)
