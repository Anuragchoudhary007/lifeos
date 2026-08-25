from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.repositories.study_goal_repository import (
    StudyGoalRepository,
)
from backend.timezone import current_local_date


class StudyGoalService:
    """Persistent weekly study goals."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = StudyGoalRepository(db)

    @staticmethod
    def get_week_start(day: date | None = None) -> date:
        if day is None:
            day = current_local_date()

        return day - timedelta(days=day.weekday())

    def get_current_goal(self, user_id: int):
        week_start = self.get_week_start()

        return self.repository.get_for_week(
            user_id,
            week_start,
        )

    def save_current_goal(
        self,
        user_id: int,
        target_hours: float,
    ):

        if target_hours <= 0:
            raise ValueError(
                "Target hours must be greater than zero."
            )

        week_start = self.get_week_start()

        try:
            goal = self.repository.create_or_update(
                user_id=user_id,
                week_start=week_start,
                target_hours=target_hours,
            )
            self.db.commit()
            self.db.refresh(goal)
            return goal
        except Exception:
            self.db.rollback()
            raise
