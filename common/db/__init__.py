from aiohttp.web import Application as AiohttpApplication
from common.db.core import Database


def setup_database(app: AiohttpApplication):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
