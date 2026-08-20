import logging
import os
import sys


DEFAULT_LOG_LEVEL = "INFO"


def get_log_level() -> int:
    """Return the configured application log level."""

    level_name = os.getenv(
        "FINSIGHT_LOG_LEVEL",
        DEFAULT_LOG_LEVEL,
    ).upper()

    level = getattr(logging, level_name, None)

    if not isinstance(level, int):
        raise ValueError(
            f"Invalid FINSIGHT_LOG_LEVEL: {level_name}"
        )

    return level


def configure_logging() -> None:
    """Configure application-wide FinSight logging."""

    logging.basicConfig(
        level=get_log_level(),
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named FinSight application logger."""

    return logging.getLogger(name)
