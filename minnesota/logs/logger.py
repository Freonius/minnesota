"""Loggers"""

from os import getcwd
from logging import Logger, getLogger, StreamHandler, INFO, DEBUG, Formatter
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Annotated, TextIO

from fastapi import Depends, Request

cwd: Path = Path(getcwd())

if not cwd.exists():
    cwd.mkdir()

log_dir: Path = cwd.joinpath("logs")

if not log_dir.exists():
    log_dir.mkdir()

log_file: Path = log_dir.joinpath("api.log")

logger: Logger = getLogger("api")
logger.setLevel(DEBUG if __debug__ else INFO)

handler: StreamHandler[TextIO] = StreamHandler()
handler.setLevel(DEBUG if __debug__ else INFO)

formatter: Formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)

logger.addHandler(handler)

file_handler: RotatingFileHandler = RotatingFileHandler(
    log_file, maxBytes=1024 * 1024 * 10
)
file_handler.setLevel(DEBUG if __debug__ else INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def _get_logger(request: Request) -> Logger:
    """Get logger"""
    logger.info(f"[{request.method}] {request.url}")
    return logger


Log = Annotated[Logger, Depends(_get_logger)]

__all__ = ["logger", "Log"]
