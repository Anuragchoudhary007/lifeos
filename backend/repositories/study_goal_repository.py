from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.study_goal import StudyGoal


class StudyGoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_for_week(
        self,
        user_id: int,
        week_start: date,
    ) -> StudyGoal | None:

        stmt = select(StudyGoal).where(
            StudyGoal.user_id == user_id,
            StudyGoal.week_start == week_start,
        )

        return self.db.scalars(stmt).first()

    def create_or_update(
        self,
        user_id: int,
        week_start: date,
        target_hours: float,
    ) -> StudyGoal:

        goal = self.get_for_week(
            user_id,
            week_start,
        )

        if goal is None:

            goal = StudyGoal(
                user_id=user_id,
                week_start=week_start,
                target_hours=target_hours,
            )

            self.db.add(goal)

        else:

            goal.target_hours = target_hours

        return goal
