from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.database import enable_sqlite_foreign_keys
from backend.models import DailyLog, StudySession, Subject, User
from backend.repositories.study_repository import StudyRepository
from backend.services.study_analytics_service import StudyAnalyticsService
from backend.services.study_service import StudyService


def test_sqlite_foreign_keys_are_enabled_for_isolated_connections(db: Session) -> None:
    event.listen(db.bind, "connect", enable_sqlite_foreign_keys)
    db.bind.dispose()

    with db.bind.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


def test_duration_constraint_rejects_non_positive_values(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    daily_log = DailyLog(user_id=user.id, log_date=date(2026, 8, 25))
    db.add(daily_log)
    db.commit()

    db.add(
        StudySession(
            daily_log_id=daily_log.id,
            subject_id=subjects["Math"].id,
            topic="Invalid duration",
            started_at=datetime(2026, 8, 25, 9, 0),
            ended_at=datetime(2026, 8, 25, 9, 0),
            duration_minutes=0,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


@pytest.mark.parametrize(
    ("topic", "focus_score", "subject_id", "message"),
    [
        ("   ", 8, 1, "Topic is required"),
        ("Valid", 11, 1, "Focus score must be between 1 and 10"),
        ("Valid", 8, 999, "Subject not found"),
    ],
)
def test_service_validates_topic_focus_and_subject(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
    topic: str,
    focus_score: int | None,
    subject_id: int,
    message: str,
) -> None:
    if subject_id == 1:
        subject_id = subjects["Math"].id

    with pytest.raises(ValueError, match=message):
        StudyService(db).create_session_for_user(
            user_id=user.id,
            study_date=date(2026, 8, 25),
            subject_id=subject_id,
            topic=topic,
            started_at=datetime(2026, 8, 25, 9, 0),
            ended_at=datetime(2026, 8, 25, 10, 0),
            focus_score=focus_score,
            notes=None,
        )


def test_service_validates_user_and_local_study_date(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    service = StudyService(db)

    with pytest.raises(ValueError, match="User not found"):
        service.create_session_for_user(
            user_id=999,
            study_date=date(2026, 8, 25),
            subject_id=subjects["Math"].id,
            topic="Valid",
            started_at=datetime(2026, 8, 25, 9, 0),
            ended_at=datetime(2026, 8, 25, 10, 0),
            focus_score=8,
            notes=None,
        )

    with pytest.raises(ValueError, match="Study date must match"):
        service.create_session_for_user(
            user_id=user.id,
            study_date=date(2026, 8, 25),
            subject_id=subjects["Math"].id,
            topic="Valid",
            started_at=datetime(2026, 8, 25, 18, 45, tzinfo=UTC),
            ended_at=datetime(2026, 8, 25, 19, 45, tzinfo=UTC),
            focus_score=8,
            notes=None,
        )


def test_service_normalizes_aware_datetimes_to_configured_local_time(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    created = StudyService(db).create_session_for_user(
        user_id=user.id,
        study_date=date(2026, 8, 26),
        subject_id=subjects["Math"].id,
        topic="Timezone conversion",
        started_at=datetime(2026, 8, 25, 18, 45, tzinfo=UTC),
        ended_at=datetime(2026, 8, 25, 19, 45, tzinfo=UTC),
        focus_score=8,
        notes=None,
    )

    assert created.started_at == datetime(2026, 8, 26, 0, 15)
    assert created.ended_at == datetime(2026, 8, 26, 1, 15)


def test_sql_aggregations_observe_month_and_week_boundaries(
    db: Session,
    make_study_session,
    monkeypatch,
) -> None:
    make_study_session(date(2026, 8, 31), duration_minutes=120)
    make_study_session(date(2026, 9, 1), duration_minutes=60)
    make_study_session(date(2026, 9, 2), duration_minutes=30)
    monkeypatch.setattr(
        "backend.services.study_analytics_service.current_local_date",
        lambda: date(2026, 9, 2),
    )

    analytics = StudyAnalyticsService(db)

    assert analytics.week_hours() == 3.5
    assert analytics.month_hours() == 1.5


def test_sql_subject_and_focus_aggregations(
    db: Session,
    make_study_session,
) -> None:
    make_study_session(date(2026, 8, 1), subject_name="Math", duration_minutes=60, focus_score=6)
    make_study_session(date(2026, 8, 1), subject_name="Math", duration_minutes=30, focus_score=10)
    make_study_session(date(2026, 8, 2), subject_name="Physics", duration_minutes=120, focus_score=None)

    analytics = StudyAnalyticsService(db)

    assert analytics.subject_distribution() == {"Math": 1.5, "Physics": 2.0}
    assert analytics.focus_trend() == {"01 Aug": 8.0}


def test_study_repository_eager_loads_subjects_without_n_plus_one_queries(
    db: Session,
    make_study_session,
) -> None:
    make_study_session(date(2026, 8, 1), subject_name="Math")
    make_study_session(date(2026, 8, 2), subject_name="Physics")
    statements: list[str] = []

    def collect_selects(conn, cursor, statement, parameters, context, executemany) -> None:
        del conn, cursor, parameters, context, executemany
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(db.bind, "after_cursor_execute", collect_selects)
    try:
        sessions = StudyRepository(db).get_all()
        [session.subject.name for session in sessions]
    finally:
        event.remove(db.bind, "after_cursor_execute", collect_selects)

    assert len(statements) == 2
    assert all(session.subject is not None for session in sessions)
