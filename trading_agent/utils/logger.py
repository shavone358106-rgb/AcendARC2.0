"""Structured logging setup using loguru."""
import sys
from pathlib import Path
from loguru import logger as _logger


def setup_logger(level: str = "INFO", log_dir: Path | None = None) -> None:
    _logger.remove()
    _logger.add(sys.stderr, level=level, colorize=True,
                format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan> - {message}")
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        _logger.add(log_dir / "agent_{time:YYYY-MM-DD}.log", rotation="00:00", retention="30 days",
                    level=level, serialize=False)


logger = _logger
