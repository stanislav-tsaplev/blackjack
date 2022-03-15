from aiohttp.web_app import Application

from admin_app.auth.routes import setup_routes as setup_auth_routes
from admin_app.game_info.routes import setup_routes as setup_game_info_routes


def setup_routes(app: Application):

    setup_auth_routes(app)
    setup_game_info_routes(app)
