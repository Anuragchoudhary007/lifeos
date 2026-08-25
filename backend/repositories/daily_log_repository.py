from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.daily_log import DailyLog


class DailyLogRepository:
    """Repository for daily log queries and persistence."""

    def __init__(self, db: Session):
        self.db = db

    def get_for_user_and_date(
        self,
        user_id: int,
        log_date: date,
    ) -> DailyLog | None:
        stmt = select(DailyLog).where(
            DailyLog.user_id == user_id,
            DailyLog.log_date == log_date,
        )
        return self.db.scalars(stmt).first()

    def get_by_id(self, daily_log_id: int) -> DailyLog | None:
        return self.db.get(DailyLog, daily_log_id)

    def create(self, daily_log: DailyLog) -> DailyLog:
        self.db.add(daily_log)
        return daily_log
