from app.bot.manager import BotManager


def setup_bot_manager(app: "Application"):
    app.bot_manager = BotManager(app)
    app.on_startup.append(app.bot_manager.restore_opened_games)