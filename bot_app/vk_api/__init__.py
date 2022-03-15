from bot_app.vk_api.accessor import VkApiAccessor


def setup_vk_api(app: "BotApplication"):
    app.vk_api = VkApiAccessor(app)