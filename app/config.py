import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class DbConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    bot: BotConfig = None
    db: DbConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as config_file:
        config_data = yaml.safe_load(config_file)

    app.config = Config(
        session=SessionConfig(**config_data["session"]),
        admin=AdminConfig(**config_data["admin"]),
        bot=BotConfig(**config_data["bot"]),
        db=DbConfig(**config_data["db"]),
    )