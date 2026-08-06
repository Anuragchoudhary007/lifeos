"""
Daily log model.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base_model import BaseModel


class DailyLog(BaseModel):
    """Represents one day in the user's life."""

    __tablename__ = "daily_logs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    mood: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    energy: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="daily_logs",
    )