"""
Study repository.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.study_session import StudySession


class StudyRepository:
    """Repository for study session operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, study_session: StudySession) -> StudySession:
        self.db.add(study_session)
        return study_session

    def get_all(self) -> list[StudySession]:
        stmt = (
            select(StudySession)
            .options(selectinload(StudySession.subject))
            .order_by(StudySession.started_at.desc())
        )
        return list(self.db.scalars(stmt).all())
