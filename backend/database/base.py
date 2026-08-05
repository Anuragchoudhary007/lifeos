"""
LifeOS Declarative Base

Base class for all SQLAlchemy models.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""