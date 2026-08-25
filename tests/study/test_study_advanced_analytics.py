from __future__ import annotations

from datetime import date, timedelta

from backend.services.study_advanced_analytics import AdvancedStudyAnalytics
from backend.services.study_analytics_service import StudyAnalyticsService


def test_consistency_calculation_includes_inactive_days_between_sessions(
    db,
    make_study_session,
) -> None:
    start = date(2026, 8, 1)
    make_study_session(start)
    make_study_session(start + timedelta(days=2))
    make_study_session(start + timedelta(days=4))

    analytics = AdvancedStudyAnalytics(StudyAnalyticsService(db).get_sessions())

    assert analytics.consistency_score() == 60.0


def test_average_focus_ignores_sessions_without_a_focus_score(
    db,
    make_study_session,
) -> None:
    study_date = date(2026, 8, 1)
    make_study_session(study_date, focus_score=6)
    make_study_session(study_date + timedelta(days=1), focus_score=10)
    make_study_session(study_date + timedelta(days=2), focus_score=None)

    analytics = AdvancedStudyAnalytics(StudyAnalyticsService(db).get_sessions())

    assert analytics.average_focus() == 8.0
