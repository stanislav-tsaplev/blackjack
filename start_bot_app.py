from pathlib import Path

from bot_app import create_bot_app
from aiohttp.web import run_app


CONFIG_PATH = Path(__file__).parent / "config.yaml"

if __name__ == "__main__":
    run_app(
        create_bot_app(config_path=CONFIG_PATH)
    )
