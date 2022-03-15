from common.logging_utils import setup_logging
from common.config import setup_config
from common.db import setup_database
from bot_app.vk_api import setup_vk_api
from bot_app.store import setup_bot_store
from bot_app.core import setup_bot_manager
from bot_app.base_utils import BotApplication


app = BotApplication()

def create_bot_app(config_path: str) -> BotApplication:
    setup_logging()
    setup_config(app, config_path)

    setup_vk_api(app)
    setup_database(app)
    setup_bot_store(app)
    setup_bot_manager(app)

    return app
