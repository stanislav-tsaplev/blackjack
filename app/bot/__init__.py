from app.bot.manager import BotManager


def setup_bot_manager(app: "Application"):
    app.bot_manager = BotManager(app)