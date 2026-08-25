from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base_model import BaseModel


class StudyGoal(BaseModel):
    """Weekly study goal."""

    __tablename__ = "study_goals"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    week_start: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    target_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="study_goals",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "week_start",
            name="uq_user_study_goal_week",
        ),
    )
