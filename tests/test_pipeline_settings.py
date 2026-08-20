from pathlib import Path

import pytest

from finsight.config.settings import (
    get_database_settings,
    get_pipeline_settings,
)


def test_pipeline_settings_use_defaults(monkeypatch):
    monkeypatch.delenv(
        "FINSIGHT_SOURCE_PATH",
        raising=False,
    )
    monkeypatch.delenv(
        "FINSIGHT_PROCESSED_PATH",
        raising=False,
    )
    monkeypatch.delenv(
        "FINSIGHT_REJECTED_PATH",
        raising=False,
    )

    settings = get_pipeline_settings()

    assert settings.source_path == Path(
        "data/raw/financial/financials_dirty.csv"
    )
    assert settings.processed_path == Path(
        "data/processed/financials.csv"
    )
    assert settings.rejected_path == Path(
        "data/rejected/financials.csv"
    )


def test_pipeline_settings_use_environment_overrides(
    monkeypatch,
):
    monkeypatch.setenv(
        "FINSIGHT_SOURCE_PATH",
        "/tmp/input.csv",
    )
    monkeypatch.setenv(
        "FINSIGHT_PROCESSED_PATH",
        "/tmp/processed.csv",
    )
    monkeypatch.setenv(
        "FINSIGHT_REJECTED_PATH",
        "/tmp/rejected.csv",
    )

    settings = get_pipeline_settings()

    assert settings.source_path == Path(
        "/tmp/input.csv"
    )
    assert settings.processed_path == Path(
        "/tmp/processed.csv"
    )
    assert settings.rejected_path == Path(
        "/tmp/rejected.csv"
    )


def test_database_settings_use_environment(
    monkeypatch,
):
    monkeypatch.setenv(
        "POSTGRES_HOST",
        "db.example.com",
    )
    monkeypatch.setenv(
        "POSTGRES_PORT",
        "5433",
    )
    monkeypatch.setenv(
        "POSTGRES_DB",
        "finsight",
    )
    monkeypatch.setenv(
        "POSTGRES_USER",
        "finsight_user",
    )
    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "secret",
    )

    settings = get_database_settings()

    assert settings.host == "db.example.com"
    assert settings.port == 5433
    assert settings.database == "finsight"
    assert settings.user == "finsight_user"
    assert settings.password == "secret"


@pytest.mark.parametrize(
    "missing_variable",
    [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_PORT",
    ],
)
def test_database_settings_reject_missing_required_variables(
    monkeypatch,
    missing_variable,
):
    monkeypatch.setenv(
        "POSTGRES_HOST",
        "localhost",
    )
    monkeypatch.setenv(
        "POSTGRES_DB",
        "finsight",
    )
    monkeypatch.setenv(
        "POSTGRES_USER",
        "finsight_user",
    )
    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "secret",
    )
    monkeypatch.setenv(
        "POSTGRES_PORT",
        "5432",
    )

    monkeypatch.delenv(
        missing_variable,
        raising=False,
    )

    with pytest.raises(RuntimeError, match="Missing required environment variables"):
        get_database_settings()


def test_database_settings_default_host(
    monkeypatch,
):
    monkeypatch.delenv(
        "POSTGRES_HOST",
        raising=False,
    )
    monkeypatch.setenv(
        "POSTGRES_DB",
        "finsight",
    )
    monkeypatch.setenv(
        "POSTGRES_USER",
        "finsight_user",
    )
    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "secret",
    )
    monkeypatch.setenv(
        "POSTGRES_PORT",
        "5432",
    )

    settings = get_database_settings()

    assert settings.host == "localhost"


def test_database_settings_reject_invalid_port(
    monkeypatch,
):
    monkeypatch.setenv(
        "POSTGRES_HOST",
        "localhost",
    )
    monkeypatch.setenv(
        "POSTGRES_DB",
        "finsight",
    )
    monkeypatch.setenv(
        "POSTGRES_USER",
        "finsight_user",
    )
    monkeypatch.setenv(
        "POSTGRES_PASSWORD",
        "secret",
    )
    monkeypatch.setenv(
        "POSTGRES_PORT",
        "not-a-number",
    )

    with pytest.raises(ValueError):
        get_database_settings()
