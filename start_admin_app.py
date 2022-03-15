from pathlib import Path

from admin_app import create_admin_app
from aiohttp.web import run_app


CONFIG_PATH = Path(__file__).parent / "config.yaml"

if __name__ == "__main__":
    run_app(
        create_admin_app(config_path=CONFIG_PATH)
    )
