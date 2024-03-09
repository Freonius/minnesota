"""Shell utils"""

from logging import Logger
from os import environ
from pathlib import Path
from subprocess import run as subrun  # nosec
from threading import Thread


def run_command(
    *cmd: str,
    background: bool = True,
    check: bool = False,
    cwd: str | None | Path = None,
    logger: Logger | None = None,
) -> None:
    """Run a command."""

    def runner() -> None:
        """Run the command."""
        full_cmd: str = " ".join(cmd)
        if logger is not None:
            logger.info(f"Running: {full_cmd}")
        else:
            print(f"Running: {full_cmd}")
        subrun(full_cmd, check=check, env=environ, cwd=cwd, shell=True)  # nosec

    if background:
        Thread(target=runner).start()
    else:
        runner()


__all__ = ("run_command",)
