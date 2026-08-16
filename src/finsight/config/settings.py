import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str


def get_database_settings() -> DatabaseSettings:
    required = {
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
        host=os.getenv(
            "POSTGRES_HOST",
            "localhost",
        ),
        port=int(required["POSTGRES_PORT"]),
        database=required["POSTGRES_DB"],
        user=required["POSTGRES_USER"],
        password=required["POSTGRES_PASSWORD"],
    )
