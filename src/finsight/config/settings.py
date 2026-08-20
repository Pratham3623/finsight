import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str


@dataclass(frozen=True)
class PipelineSettings:
    source_path: Path
    processed_path: Path
    rejected_path: Path


def get_database_settings() -> DatabaseSettings:
    required = {
        "POSTGRES_HOST": os.getenv(
            "POSTGRES_HOST",
            "localhost",
        ),
        "POSTGRES_DB": os.getenv("POSTGRES_DB"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
    }

    missing = [
        key
        for key, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
        )

    return DatabaseSettings(
        host=required["POSTGRES_HOST"],
        port=int(required["POSTGRES_PORT"]),
        database=required["POSTGRES_DB"],
        user=required["POSTGRES_USER"],
        password=required["POSTGRES_PASSWORD"],
    )


def get_pipeline_settings() -> PipelineSettings:
    return PipelineSettings(
        source_path=Path(
            os.getenv(
                "FINSIGHT_SOURCE_PATH",
                "data/raw/financial/financials_dirty.csv",
            )
        ),
        processed_path=Path(
            os.getenv(
                "FINSIGHT_PROCESSED_PATH",
                "data/processed/financials.csv",
            )
        ),
        rejected_path=Path(
            os.getenv(
                "FINSIGHT_REJECTED_PATH",
                "data/rejected/financials.csv",
            )
        ),
    )
