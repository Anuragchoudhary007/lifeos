from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import StudyGoal, User
from backend.services.study_goal_service import StudyGoalService


def test_week_start_calculation_uses_monday() -> None:
    assert StudyGoalService.get_week_start(date(2026, 8, 30)) == date(2026, 8, 24)
    assert StudyGoalService.get_week_start(date(2026, 8, 24)) == date(2026, 8, 24)


def test_weekly_goal_persists_and_updates_for_the_same_week(
    db: Session,
    user: User,
) -> None:
    service = StudyGoalService(db)
    week_start = service.get_week_start()

    created_goal = service.save_current_goal(user.id, 12.0)
    updated_goal = service.save_current_goal(user.id, 15.0)

    assert created_goal.id == updated_goal.id
    assert updated_goal.target_hours == 15.0
    assert service.get_current_goal(user.id).target_hours == 15.0
    assert db.scalar(select(func.count()).select_from(StudyGoal)) == 1
    assert updated_goal.week_start == week_start
