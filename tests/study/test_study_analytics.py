from __future__ import annotations

from datetime import date, timedelta

from backend.services.study_analytics_service import StudyAnalyticsService


def test_weekly_hours_include_only_current_week(
    db,
    make_study_session,
) -> None:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    make_study_session(monday, duration_minutes=60)
    make_study_session(today, duration_minutes=90)
    make_study_session(monday - timedelta(days=1), duration_minutes=120)

    assert StudyAnalyticsService(db).week_hours() == 2.5


def test_monthly_hours_include_only_current_month(
    db,
    make_study_session,
) -> None:
    today = date.today()
    first_day = today.replace(day=1)
    previous_month_day = first_day - timedelta(days=1)
    make_study_session(first_day, duration_minutes=60)
    make_study_session(today, duration_minutes=120)
    make_study_session(previous_month_day, duration_minutes=180)

    assert StudyAnalyticsService(db).month_hours() == 3.0


def test_current_streak_counts_consecutive_active_days(
    db,
    make_study_session,
) -> None:
    today = date.today()
    make_study_session(today, duration_minutes=30)
    make_study_session(today - timedelta(days=1), duration_minutes=30)
    make_study_session(today - timedelta(days=2), duration_minutes=30)
    make_study_session(today - timedelta(days=4), duration_minutes=30)

    assert StudyAnalyticsService(db).current_streak() == 3


def test_subject_distribution_aggregates_duration_by_subject(
    db,
    make_study_session,
) -> None:
    study_date = date.today()
    make_study_session(study_date, subject_name="Math", duration_minutes=60)
    make_study_session(study_date, subject_name="Math", duration_minutes=30)
    make_study_session(study_date, subject_name="Physics", duration_minutes=120)

    assert StudyAnalyticsService(db).subject_distribution() == {
        "Math": 1.5,
        "Physics": 2.0,
    }
