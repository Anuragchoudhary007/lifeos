"""
LifeOS Database Session

Provides database sessions for interacting with the database.
"""

from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from backend.database.database import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)