from __future__ import annotations

from datetime import date, datetime, time

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import DailyLog, StudySession, Subject, User
from backend.services.study_service import StudyService


def test_create_study_session_persists_duration(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    daily_log = DailyLog(user_id=user.id, log_date=date(2026, 8, 25))
    db.add(daily_log)
    db.commit()
    db.refresh(daily_log)

    session = StudyService(db).create_session(
        daily_log_id=daily_log.id,
        subject_id=subjects["Math"].id,
        topic="Calculus",
        started_at=datetime(2026, 8, 25, 9, 0),
        ended_at=datetime(2026, 8, 25, 10, 30),
        focus_score=9,
        notes="Derivatives",
    )

    assert session.id is not None
    assert session.duration_minutes == 90
    assert session.topic == "Calculus"
    assert session.focus_score == 9


@pytest.mark.parametrize(
    ("started_at", "ended_at"),
    [
        (datetime(2026, 8, 25, 9, 0), datetime(2026, 8, 25, 9, 0)),
        (datetime(2026, 8, 25, 10, 0), datetime(2026, 8, 25, 9, 0)),
    ],
)
def test_create_study_session_rejects_non_positive_duration(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
    started_at: datetime,
    ended_at: datetime,
) -> None:
    daily_log = DailyLog(user_id=user.id, log_date=date(2026, 8, 25))
    db.add(daily_log)
    db.commit()

    with pytest.raises(ValueError, match="End time must be after start time"):
        StudyService(db).create_session(
            daily_log_id=daily_log.id,
            subject_id=subjects["Math"].id,
            topic="Calculus",
            started_at=started_at,
            ended_at=ended_at,
            focus_score=8,
            notes=None,
        )


def test_create_session_for_user_creates_daily_log_and_session_atomically(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    created = StudyService(db).create_session_for_user(
        user_id=user.id,
        study_date=date(2026, 8, 25),
        subject_id=subjects["Math"].id,
        topic="Calculus",
        started_at=datetime(2026, 8, 25, 9, 0),
        ended_at=datetime(2026, 8, 25, 10, 30),
        focus_score=9,
        notes="Derivatives",
    )

    daily_log = db.scalar(select(DailyLog))

    assert created.id is not None
    assert created.daily_log_id == daily_log.id
    assert db.scalar(select(func.count()).select_from(StudySession)) == 1


def test_create_session_for_user_creates_missing_daily_log(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    created = StudyService(db).create_session_for_user(
        user_id=user.id,
        study_date=date(2026, 8, 26),
        subject_id=subjects["Math"].id,
        topic="Calculus",
        started_at=datetime(2026, 8, 26, 9, 0),
        ended_at=datetime(2026, 8, 26, 10, 0),
        focus_score=8,
        notes=None,
    )

    daily_log = db.scalar(select(DailyLog))

    assert daily_log is not None
    assert daily_log.log_date == date(2026, 8, 26)
    assert created.daily_log_id == daily_log.id


def test_create_session_for_user_reuses_existing_daily_log(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    daily_log = DailyLog(user_id=user.id, log_date=date(2026, 8, 25))
    db.add(daily_log)
    db.commit()

    created = StudyService(db).create_session_for_user(
        user_id=user.id,
        study_date=date(2026, 8, 25),
        subject_id=subjects["Math"].id,
        topic="Calculus",
        started_at=datetime(2026, 8, 25, 9, 0),
        ended_at=datetime(2026, 8, 25, 10, 0),
        focus_score=8,
        notes=None,
    )

    assert created.daily_log_id == daily_log.id
    assert db.scalar(select(func.count()).select_from(DailyLog)) == 1


def test_create_session_for_user_rolls_back_when_session_creation_fails(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = StudyService(db)

    def fail_to_create(_: StudySession) -> StudySession:
        raise RuntimeError("Session creation failed")

    monkeypatch.setattr(service.repository, "create", fail_to_create)

    with pytest.raises(RuntimeError, match="Session creation failed"):
        service.create_session_for_user(
            user_id=user.id,
            study_date=date(2026, 8, 25),
            subject_id=subjects["Math"].id,
            topic="Calculus",
            started_at=datetime(2026, 8, 25, 9, 0),
            ended_at=datetime(2026, 8, 25, 10, 0),
            focus_score=8,
            notes=None,
        )

    assert db.scalar(select(func.count()).select_from(DailyLog)) == 0
    assert db.scalar(select(func.count()).select_from(StudySession)) == 0


def test_create_session_for_user_rejects_invalid_times(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> None:
    with pytest.raises(ValueError, match="End time must be after start time"):
        StudyService(db).create_session_for_user(
            user_id=user.id,
            study_date=date(2026, 8, 25),
            subject_id=subjects["Math"].id,
            topic="Calculus",
            started_at=datetime(2026, 8, 25, 10, 0),
            ended_at=datetime(2026, 8, 25, 9, 0),
            focus_score=8,
            notes=None,
        )
