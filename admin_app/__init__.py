from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from common.logging_utils import setup_logging
from common.config import setup_config
from common.db import setup_database
from admin_app.store import setup_admin_store
from admin_app.web.routes import setup_routes
from admin_app.web.middlewares import setup_middlewares
from admin_app.base_classes import AdminApplication


app = AdminApplication()

def create_admin_app(config_path: str) -> AdminApplication:
    setup_logging()
    setup_config(app, config_path)

    setup_aiohttp_apispec(
        app, title="Vk Blackjack Bot", url="/docs/json", swagger_path="/docs"
    )
    setup_session(app, EncryptedCookieStorage(app.config.session.key))
    setup_routes(app)
    setup_middlewares(app)

    setup_database(app)
    setup_admin_store(app)

    return app
