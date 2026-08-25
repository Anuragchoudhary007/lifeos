"""
Study service.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from backend.models.daily_log import DailyLog
from backend.models.study_session import StudySession
from backend.repositories.daily_log_repository import DailyLogRepository
from backend.repositories.study_repository import StudyRepository
from backend.repositories.subject_repository import SubjectRepository
from backend.repositories.user_repository import UserRepository
from backend.timezone import to_local_datetime, to_storage_datetime


class StudyService:
    """Business logic for study sessions."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = StudyRepository(db)
        self.daily_log_repository = DailyLogRepository(db)
        self.subject_repository = SubjectRepository(db)
        self.user_repository = UserRepository(db)

    def _validate_session_input(
        self,
        topic: str,
        started_at: datetime,
        ended_at: datetime,
        focus_score: int | None,
        subject_id: int,
    ) -> tuple[datetime, datetime, int]:
        if not topic.strip():
            raise ValueError("Topic is required.")

        if focus_score is not None and not 1 <= focus_score <= 10:
            raise ValueError("Focus score must be between 1 and 10.")

        if self.subject_repository.get_by_id(subject_id) is None:
            raise ValueError("Subject not found.")

        started_at = to_storage_datetime(started_at)
        ended_at = to_storage_datetime(ended_at)

        if ended_at <= started_at:
            raise ValueError(
                "End time must be after start time."
            )

        duration = int((ended_at - started_at).total_seconds() // 60)
        if duration <= 0:
            raise ValueError("Study session duration must be at least one minute.")

        return started_at, ended_at, duration

    def _build_session(
        self,
        daily_log_id: int,
        subject_id: int,
        topic: str,
        started_at: datetime,
        ended_at: datetime,
        focus_score: int | None,
        notes: str | None,
        duration: int,
    ) -> StudySession:
        return StudySession(
            daily_log_id=daily_log_id,
            subject_id=subject_id,
            topic=topic,
            started_at=started_at,
            ended_at=ended_at,
            duration_minutes=duration,
            focus_score=focus_score,
            notes=notes,
        )

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
        if self.daily_log_repository.get_by_id(daily_log_id) is None:
            raise ValueError("Daily log not found.")

        started_at, ended_at, duration = self._validate_session_input(
            topic,
            started_at,
            ended_at,
            focus_score,
            subject_id,
        )
        session = self._build_session(
            daily_log_id,
            subject_id,
            topic,
            started_at,
            ended_at,
            focus_score,
            notes,
            duration,
        )

        try:
            self.repository.create(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception:
            self.db.rollback()
            raise

    def create_session_for_user(
        self,
        user_id: int,
        study_date: date,
        subject_id: int,
        topic: str,
        started_at: datetime,
        ended_at: datetime,
        focus_score: int | None,
        notes: str | None,
    ) -> StudySession:
        """Create a study session and its daily log in one transaction."""
        if self.user_repository.get_by_id(user_id) is None:
            raise ValueError("User not found.")

        started_at, ended_at, duration = self._validate_session_input(
            topic,
            started_at,
            ended_at,
            focus_score,
            subject_id,
        )

        if to_local_datetime(started_at).date() != study_date:
            raise ValueError(
                "Study date must match the session start date in the configured timezone."
            )

        try:
            daily_log = self.daily_log_repository.get_for_user_and_date(
                user_id,
                study_date,
            )

            if daily_log is None:
                daily_log = DailyLog(
                    user_id=user_id,
                    log_date=study_date,
                )
                self.daily_log_repository.create(daily_log)
                self.db.flush()

            session = self._build_session(
                daily_log.id,
                subject_id,
                topic,
                started_at,
                ended_at,
                focus_score,
                notes,
                duration,
            )
            self.repository.create(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception:
            self.db.rollback()
            raise

    def get_sessions(self):
        return self.repository.get_all()
