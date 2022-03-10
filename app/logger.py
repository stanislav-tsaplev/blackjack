from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from app.web.app import Application


def setup_logging(_: "Application") -> None:
    logging.basicConfig(level=logging.INFO)
