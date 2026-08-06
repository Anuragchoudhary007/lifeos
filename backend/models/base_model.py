"""
Base model for all database models.
"""

from __future__ import annotations

from backend.database.base import Base
from backend.models.mixins import IDMixin, TimestampMixin, UUIDMixin


class BaseModel(
    Base,
    IDMixin,
    UUIDMixin,
    TimestampMixin,
):
    """Abstract base model."""

    __abstract__ = True