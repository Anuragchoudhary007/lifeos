from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from backend.models.study_session import StudySession


class AdvancedStudyAnalytics:

    def __init__(self, sessions: list[StudySession]):
        self.sessions = sessions

    def daily_hours(self) -> dict[date, float]:
        result = defaultdict(float)

        for session in self.sessions:
            result[session.started_at.date()] += (
                session.duration_minutes / 60
            )

        return dict(result)

    def weekday_hours(self) -> dict[str, float]:
        result = {
            day: 0.0
            for day in [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        }

        for session in self.sessions:
            day = session.started_at.strftime("%A")

            result[day] += (
                session.duration_minutes / 60
            )

        return result

    def hourly_distribution(self) -> dict[int, float]:
        result = defaultdict(float)

        for session in self.sessions:
            hour = session.started_at.hour

            result[hour] += (
                session.duration_minutes / 60
            )

        return dict(sorted(result.items()))

    def rolling_7_day_average(
        self,
    ) -> list[tuple[date, float]]:

        daily = self.daily_hours()

        if not daily:
            return []

        start = min(daily)
        end = max(daily)

        results = []

        current = start

        while current <= end:

            total = 0.0

            for i in range(7):
                day = current - timedelta(days=i)
                total += daily.get(day, 0.0)

            results.append(
                (
                    current,
                    total / 7,
                )
            )

            current += timedelta(days=1)

        return results