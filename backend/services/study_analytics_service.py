from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.study_session import StudySession


class StudyAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_sessions(self) -> list[StudySession]:
        stmt = select(StudySession).order_by(
            StudySession.started_at.asc()
        )
        return list(self.db.scalars(stmt).all())

    def _sessions_for_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[StudySession]:
        return [
            session
            for session in self.get_sessions()
            if start_date
            <= session.started_at.date()
            <= end_date
        ]

    @staticmethod
    def total_hours(sessions: list[StudySession]) -> float:
        minutes = sum(
            session.duration_minutes
            for session in sessions
        )
        return minutes / 60

    def today_hours(self) -> float:
        today = date.today()

        return self.total_hours(
            self._sessions_for_date_range(today, today)
        )

    def week_hours(self) -> float:
        today = date.today()
        monday = today - timedelta(days=today.weekday())

        return self.total_hours(
            self._sessions_for_date_range(monday, today)
        )

    def month_hours(self) -> float:
        today = date.today()
        first_day = today.replace(day=1)

        return self.total_hours(
            self._sessions_for_date_range(first_day, today)
        )

    def current_streak(self) -> int:
        sessions = self.get_sessions()

        active_days = {
            session.started_at.date()
            for session in sessions
        }

        today = date.today()

        streak = 0
        current_day = today

        while current_day in active_days:
            streak += 1
            current_day -= timedelta(days=1)

        return streak

    def weekly_trend(self) -> dict[str, float]:
        today = date.today()
        monday = today - timedelta(days=today.weekday())

        sessions = self._sessions_for_date_range(
            monday,
            today,
        )

        result = {
            (monday + timedelta(days=i)).strftime("%a"): 0.0
            for i in range(7)
        }

        for session in sessions:
            day = session.started_at.date()

            if monday <= day <= monday + timedelta(days=6):
                label = day.strftime("%a")
                result[label] += session.duration_minutes / 60

        return result

    def subject_distribution(self) -> dict[str, float]:
        result = defaultdict(float)

        for session in self.get_sessions():
            result[session.subject.name] += (
                session.duration_minutes / 60
            )

        return dict(result)

    def focus_trend(self) -> dict[str, float]:
        scores = defaultdict(list)

        for session in self.get_sessions():
            if session.focus_score is not None:
                scores[session.started_at.date()].append(
                    session.focus_score
                )

        return {
            day.strftime("%d %b"): round(
                sum(values) / len(values),
                2,
            )
            for day, values in sorted(scores.items())
        }