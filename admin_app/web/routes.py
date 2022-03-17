from aiohttp.web_app import Application

from admin_app.auth.routes import setup_routes as setup_auth_routes
from admin_app.games.routes import setup_routes as setup_games_summary_routes


def setup_routes(app: Application):

    setup_auth_routes(app)
    setup_games_summary_routes(app)
