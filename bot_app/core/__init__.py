from bot_app.core.manager import BotManager


def setup_bot_manager(app: "BotApplication"):
    app.bot_manager = BotManager(app)
    app.on_startup.append(app.bot_manager.restore_opened_games)