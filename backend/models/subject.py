"""
Subject model.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base_model import BaseModel


class Subject(BaseModel):
    """Study subject."""

    __tablename__ = "subjects"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    color: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    study_sessions = relationship(
        "StudySession",
        back_populates="subject",
    )