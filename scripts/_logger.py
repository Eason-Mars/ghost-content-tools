"""Shared rotating file logger for ghost-content-tools scripts.

Logs go to `<repo-root>/logs/ghost-publish.log` with 1MB rotation × 5 backups,
so silent failures (e.g. Supabase write skips) survive past the terminal session.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "ghost-publish.log"


def get_logger(name: str = "ghost") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)

    fh = RotatingFileHandler(_LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)
    sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(sh)

    logger.propagate = False
    return logger
