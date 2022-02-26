from app.vk_api.accessor import VkApiAccessor


def setup_vk_api(app: "Application"):
    app.vk_api = VkApiAccessor(app)