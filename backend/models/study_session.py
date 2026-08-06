"""
Study session model.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base_model import BaseModel


class StudySession(BaseModel):
    """Study session."""

    __tablename__ = "study_sessions"

    daily_log_id: Mapped[int] = mapped_column(
        ForeignKey("daily_logs.id"),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False,
        index=True,
    )

    topic: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    focus_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    daily_log = relationship(
        "DailyLog",
        back_populates="study_sessions",
    )

    subject = relationship(
        "Subject",
        back_populates="study_sessions",
    )