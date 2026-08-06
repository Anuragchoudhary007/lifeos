"""
User model.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base_model import BaseModel


class User(BaseModel):
    """Application user."""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    height_cm: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    target_weight_kg: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Asia/Kolkata",
        nullable=False,
    )