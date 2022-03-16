from dataclasses import dataclass
import yaml

from aiohttp.web import Application as AiohttpApplication


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    name: str
    token: str
    group_id: int



@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    bot: BotConfig = None


def setup_config(app: AiohttpApplication, config_path: str):
    with open(config_path, "r") as config_file:
        config_data = yaml.safe_load(config_file)

    app.config = Config(
        session=SessionConfig(**config_data["session"]),
        admin=AdminConfig(**config_data["admin"]),
        bot=BotConfig(**config_data["bot"]),
    )
