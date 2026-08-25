"""Timezone helpers for LifeOS's configured single-user timezone."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from config.settings import settings


def configured_timezone() -> ZoneInfo:
    return ZoneInfo(settings.DEFAULT_USER_TIMEZONE)


def current_local_date() -> date:
    return datetime.now(configured_timezone()).date()


def to_storage_datetime(value: datetime) -> datetime:
    """Normalize input to configured local wall time for SQLite storage.

    SQLite does not preserve timezone offsets for ``DateTime`` values. Existing
    LifeOS rows are therefore treated as configured-timezone wall-clock values.
    """
    timezone = configured_timezone()
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone).replace(tzinfo=None)


def to_local_datetime(value: datetime) -> datetime:
    """Interpret a stored value in the configured timezone."""
    timezone = configured_timezone()
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone)
    return value.astimezone(timezone)


def storage_day_bounds(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, datetime.min.time())
    return start, start + timedelta(days=1)
