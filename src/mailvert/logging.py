import logging
import sys

from mailvert.config import settings

_JSON_FORMAT = (
    '{"time":"%(asctime)s","level":"%(levelname)s",'
    '"logger":"%(name)s","message":"%(message)s"}'
)
_TEXT_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    fmt = _JSON_FORMAT if settings.log_json else _TEXT_FORMAT
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S%z"))

    root = logging.getLogger("mailvert")
    root.setLevel(settings.log_level)
    root.handlers = [handler]
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"mailvert.{name}")
