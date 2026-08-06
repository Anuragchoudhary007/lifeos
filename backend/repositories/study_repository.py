"""
Study repository.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.study_session import StudySession


class StudyRepository:
    """Repository for study session operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, study_session: StudySession) -> StudySession:
        self.db.add(study_session)
        self.db.commit()
        self.db.refresh(study_session)
        return study_session

    def get_all(self) -> list[StudySession]:
        return (
            self.db.query(StudySession)
            .order_by(StudySession.started_at.desc())
            .all()
        )