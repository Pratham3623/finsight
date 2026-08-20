import logging

import pytest

from finsight.logging.config import (
    configure_logging,
    get_log_level,
    get_logger,
)


def test_get_logger_returns_named_logger():
    logger = get_logger("finsight.test")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "finsight.test"


def test_default_log_level_is_info(monkeypatch):
    monkeypatch.delenv(
        "FINSIGHT_LOG_LEVEL",
        raising=False,
    )

    assert get_log_level() == logging.INFO


def test_log_level_can_be_configured(monkeypatch):
    monkeypatch.setenv(
        "FINSIGHT_LOG_LEVEL",
        "DEBUG",
    )

    assert get_log_level() == logging.DEBUG


def test_invalid_log_level_raises(monkeypatch):
    monkeypatch.setenv(
        "FINSIGHT_LOG_LEVEL",
        "NOT_A_LEVEL",
    )

    with pytest.raises(ValueError):
        get_log_level()


def test_configure_logging_sets_expected_level(
    monkeypatch,
):
    monkeypatch.setenv(
        "FINSIGHT_LOG_LEVEL",
        "DEBUG",
    )

    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    try:
        configure_logging()

        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) == 1

    finally:
        for handler in root_logger.handlers:
            handler.close()

        root_logger.handlers.clear()
        root_logger.handlers.extend(original_handlers)
        root_logger.setLevel(original_level)
