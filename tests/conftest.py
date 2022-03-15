from pathlib import Path
from datetime import datetime, timezone
import functools
import re

import pytest
from freezegun import freeze_time
from aioresponses import aioresponses
from gino import GinoEngine

from bot_app import setup_bot_app
from tests.fixtures.admin import *
from tests.fixtures.bot import *


TEST_CONFIG_PATH = Path(__file__).parent / "config.yaml"
DEFAULT_TIME = datetime(2020, 11, 14)

@pytest.fixture()
def freezed_time():
    freezer = freeze_time(DEFAULT_TIME)

    freezer.start()
    yield DEFAULT_TIME
    freezer.stop()


@pytest.fixture()
async def mocked_request():
    with aioresponses(passthrough=["http://127.0.0.1"]) as mock:
        yield mock

@fixture
def mocked_vk_api_long_polling(mocked_request):    
    mocked_request.get(
        re.compile(f"{VK_API_PATH}groups\.getLongPollServer.*"),
        status=200,
        payload={
            "response": {
                "key": "0f276c3cebb312d723ffd0ebfe5bae6cfb09dc42",
                "server": LONG_POLL_SERVER,
                "ts": 1
            }
        },
    )

    mocked_request.get(
        re.compile(f"{LONG_POLL_SERVER}\?act\=a_check.*"),
        timeout=True,
        # repeat=True,
        status=200,
        payload={
            "ts": 2,
            "updates": [],
        },
    )

@pytest.fixture
def app(mocked_vk_api_long_polling):
    return setup_bot_app(TEST_CONFIG_PATH)


@pytest.fixture
async def cli(aiohttp_client, app):
    client = await aiohttp_client(app)
    yield client


@pytest.fixture(autouse=True)
async def db_transaction(cli):
    db = cli.app.database.orm
    real_acquire = GinoEngine.acquire

    async with db.acquire() as conn:
        class _AcquireContext:
            __slots__ = ["_acquire", "_conn"]

            def __init__(self, acquire):
                self._acquire = acquire

            async def __aenter__(self):
                return conn

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            def __await__(self):
                return conn

        def acquire(
            self, *, timeout=None, reuse=False, lazy=False, reusable=True
        ):
            return _AcquireContext(
                functools.partial(self._acquire, timeout, reuse, lazy, reusable)
            )

        GinoEngine.acquire = acquire
        transaction = await conn.transaction()
        yield
        await transaction.rollback()
        GinoEngine.acquire = real_acquire
