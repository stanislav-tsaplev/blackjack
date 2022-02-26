from pathlib import Path

from app.web.app import setup_app
from aiohttp.web import run_app


CONFIG_PATH = Path(__file__).parent / "config.yaml"

if __name__ == "__main__":
    run_app(setup_app(config_path=CONFIG_PATH))
