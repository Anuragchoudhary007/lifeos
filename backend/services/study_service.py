"""
Study service.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.study_session import StudySession
from backend.repositories.study_repository import StudyRepository


class StudyService:
    """Business logic for study sessions."""

    def __init__(self, db: Session):
        self.repository = StudyRepository(db)

    def create_session(
        self,
        daily_log_id: int,
        subject_id: int,
        topic: str,
        started_at: datetime,
        ended_at: datetime,
        focus_score: int | None,
        notes: str | None,
    ) -> StudySession:

        duration = int((ended_at - started_at).total_seconds() // 60)

        session = StudySession(
            daily_log_id=daily_log_id,
            subject_id=subject_id,
            topic=topic,
            started_at=started_at,
            ended_at=ended_at,
            duration_minutes=duration,
            focus_score=focus_score,
            notes=notes,
        )

        return self.repository.create(session)

    def get_sessions(self):
        return self.repository.get_all()