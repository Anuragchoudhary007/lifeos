from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from backend.models.study_session import StudySession
from backend.timezone import to_local_datetime


class AdvancedStudyAnalytics:
    """Advanced analytics for study sessions."""

    def __init__(self, sessions: list[StudySession]):
        self.sessions = sessions

    # =====================================================
    # DAILY HOURS
    # =====================================================

    def daily_hours(self) -> dict[date, float]:
        result = defaultdict(float)

        for session in self.sessions:
            result[to_local_datetime(session.started_at).date()] += (
                session.duration_minutes / 60
            )

        return dict(result)

    # =====================================================
    # WEEKDAY HOURS
    # =====================================================

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
            day = to_local_datetime(session.started_at).strftime("%A")

            result[day] += (
                session.duration_minutes / 60
            )

        return result

    # =====================================================
    # HOURLY DISTRIBUTION
    # =====================================================

    def hourly_distribution(self) -> dict[int, float]:
        result = defaultdict(float)

        for session in self.sessions:
            hour = to_local_datetime(session.started_at).hour

            result[hour] += (
                session.duration_minutes / 60
            )

        return dict(sorted(result.items()))

    # =====================================================
    # 7-DAY ROLLING AVERAGE
    # =====================================================

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

                total += daily.get(
                    day,
                    0.0,
                )

            results.append(
                (
                    current,
                    total / 7,
                )
            )

            current += timedelta(days=1)

        return results

    # =====================================================
    # TOTAL HOURS
    # =====================================================

    def total_hours(self) -> float:

        total_minutes = sum(
            session.duration_minutes
            for session in self.sessions
        )

        return total_minutes / 60

    # =====================================================
    # AVERAGE FOCUS
    # =====================================================

    def average_focus(self) -> float:

        scores = [
            session.focus_score
            for session in self.sessions
            if session.focus_score is not None
        ]

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    # =====================================================
    # SUBJECT PERFORMANCE
    # =====================================================

    def subject_performance(self) -> list[dict]:

        data = defaultdict(
            lambda: {
                "hours": 0.0,
                "focus_scores": [],
                "sessions": 0,
            }
        )

        for session in self.sessions:

            subject_name = session.subject.name

            data[subject_name]["hours"] += (
                session.duration_minutes / 60
            )

            data[subject_name]["sessions"] += 1

            if session.focus_score is not None:

                data[subject_name][
                    "focus_scores"
                ].append(
                    session.focus_score
                )

        results = []

        for subject, values in data.items():

            scores = values["focus_scores"]

            average_focus = (
                sum(scores) / len(scores)
                if scores
                else 0.0
            )

            results.append(
                {
                    "Subject": subject,
                    "Hours": round(
                        values["hours"],
                        2,
                    ),
                    "Sessions": values["sessions"],
                    "Avg Focus": round(
                        average_focus,
                        2,
                    ),
                }
            )

        return sorted(
            results,
            key=lambda item: item["Hours"],
            reverse=True,
        )

    # =====================================================
    # CONSISTENCY SCORE
    # =====================================================

    def consistency_score(self) -> float:

        if not self.sessions:
            return 0.0

        daily = self.daily_hours()

        if not daily:
            return 0.0

        first_day = min(daily)
        last_day = max(daily)

        total_days = (
            last_day - first_day
        ).days + 1

        active_days = len(daily)

        return round(
            (active_days / total_days) * 100,
            1,
        )
