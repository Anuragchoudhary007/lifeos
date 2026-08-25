"""
LifeOS Database Engine

Creates the SQLAlchemy engine used throughout the application.
"""

from __future__ import annotations

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from config.settings import settings

# SQLite-specific connection arguments
connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False


engine: Engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
)


def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    """Enable SQLite foreign-key enforcement on each new connection."""
    del connection_record
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


if settings.DATABASE_URL.startswith("sqlite"):
    event.listen(engine, "connect", enable_sqlite_foreign_keys)
