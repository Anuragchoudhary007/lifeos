from __future__ import annotations

from datetime import date, timedelta

from backend.services.study_analytics_service import StudyAnalyticsService


class StudyGoalService:
    """Study goal calculations."""

    def __init__(self, analytics: StudyAnalyticsService):
        self.analytics = analytics

    def weekly_progress(self, target_hours: float) -> dict:
        actual_hours = self.analytics.week_hours()

        if target_hours <= 0:
            progress = 0.0
        else:
            progress = min(
                actual_hours / target_hours,
                1.0,
            )

        return {
            "target": target_hours,
            "actual": actual_hours,
            "remaining": max(
                target_hours - actual_hours,
                0,
            ),
            "progress": progress,
        }