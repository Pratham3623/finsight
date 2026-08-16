import psycopg

from finsight.config.settings import get_database_settings


def get_connection() -> psycopg.Connection:
    settings = get_database_settings()

    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.user,
        password=settings.password,
    )
