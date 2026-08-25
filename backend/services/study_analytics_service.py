from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.study_session import StudySession
from backend.models.subject import Subject
from backend.repositories.study_repository import StudyRepository
from backend.timezone import current_local_date, storage_day_bounds, to_local_datetime


class StudyAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = StudyRepository(db)

    def get_sessions(self) -> list[StudySession]:
        return self.repository.get_all()

    def _minutes_for_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> int:
        start, _ = storage_day_bounds(start_date)
        _, end = storage_day_bounds(end_date)
        stmt = select(func.coalesce(func.sum(StudySession.duration_minutes), 0)).where(
            StudySession.started_at >= start,
            StudySession.started_at < end,
        )
        return int(self.db.scalar(stmt) or 0)

    def today_hours(self) -> float:
        today = current_local_date()
        return self._minutes_for_date_range(today, today) / 60

    def week_hours(self) -> float:
        today = current_local_date()
        monday = today - timedelta(days=today.weekday())
        return self._minutes_for_date_range(monday, today) / 60

    def month_hours(self) -> float:
        today = current_local_date()
        first_day = today.replace(day=1)
        return self._minutes_for_date_range(first_day, today) / 60

    def current_streak(self) -> int:
        active_days = {
            to_local_datetime(started_at).date()
            for started_at in self.db.scalars(
                select(StudySession.started_at)
            ).all()
        }

        today = current_local_date()

        streak = 0
        current_day = today

        while current_day in active_days:
            streak += 1
            current_day -= timedelta(days=1)

        return streak

    def weekly_trend(self) -> dict[str, float]:
        today = current_local_date()
        monday = today - timedelta(days=today.weekday())

        result = {
            (monday + timedelta(days=i)).strftime("%a"): 0.0
            for i in range(7)
        }

        start, _ = storage_day_bounds(monday)
        _, end = storage_day_bounds(today)
        stmt = (
            select(
                func.date(StudySession.started_at),
                func.sum(StudySession.duration_minutes),
            )
            .where(
                StudySession.started_at >= start,
                StudySession.started_at < end,
            )
            .group_by(func.date(StudySession.started_at))
        )
        for day_value, minutes in self.db.execute(stmt):
            day = date.fromisoformat(day_value)
            result[day.strftime("%a")] = minutes / 60

        return result

    def subject_distribution(self) -> dict[str, float]:
        stmt = (
            select(
                Subject.name,
                func.sum(StudySession.duration_minutes),
            )
            .join(StudySession, StudySession.subject_id == Subject.id)
            .group_by(Subject.id, Subject.name)
            .order_by(Subject.name)
        )
        return {
            subject_name: minutes / 60
            for subject_name, minutes in self.db.execute(stmt)
        }

    def focus_trend(self) -> dict[str, float]:
        stmt = (
            select(
                func.date(StudySession.started_at),
                func.avg(StudySession.focus_score),
            )
            .where(StudySession.focus_score.is_not(None))
            .group_by(func.date(StudySession.started_at))
            .order_by(func.date(StudySession.started_at))
        )
        return {
            date.fromisoformat(day_value).strftime("%d %b"): round(
                average_focus,
                2,
            )
            for day_value, average_focus in self.db.execute(stmt)
        }
