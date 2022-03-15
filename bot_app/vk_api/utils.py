import re

from bot_app.vk_api.models import VkApiMessage


def build_query_url(api_path: str, api_method: str, params: dict) -> str:
    params.setdefault("v", "5.131")

    url = f"{api_path}{api_method}?" + \
        "&".join([f"{k}={v}" for k, v in params.items()])
    return url

def make_regex_for_query_url(query_url: str):
    return re.compile(
        query_url.replace(".", r"\.").replace("?", r"\?") \
                    + r"(\?([^&=]+=[^&=]+)(&[^&=]+=[^&=]+))?"
    )

def is_sent_from_chat(vk_api_message: VkApiMessage) -> bool:
    return vk_api_message.peer_id > 2_000_000_000