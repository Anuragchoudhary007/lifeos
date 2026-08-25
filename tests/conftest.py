from __future__ import annotations

from datetime import date, datetime, time, timedelta
from collections.abc import Callable

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend.database.base import Base
from backend.models import DailyLog, StudySession, Subject, User
from config.settings import settings


@pytest.fixture
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def user(db: Session) -> User:
    user = User(
        name="Test User",
        email="test-user@lifeos.local",
        timezone=settings.DEFAULT_USER_TIMEZONE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def subjects(db: Session) -> dict[str, Subject]:
    items = [Subject(name="Math"), Subject(name="Physics")]
    db.add_all(items)
    db.commit()
    return {subject.name: subject for subject in items}


@pytest.fixture
def make_study_session(
    db: Session,
    user: User,
    subjects: dict[str, Subject],
) -> Callable[..., StudySession]:
    def _make(
        session_date: date,
        *,
        subject_name: str = "Math",
        start_time: time = time(9, 0),
        duration_minutes: int = 60,
        focus_score: int | None = 8,
    ) -> StudySession:
        daily_log = db.scalars(
            select(DailyLog).where(
                DailyLog.user_id == user.id,
                DailyLog.log_date == session_date,
            )
        ).first()

        if daily_log is None:
            daily_log = DailyLog(
                user_id=user.id,
                log_date=session_date,
            )
            db.add(daily_log)
            db.flush()

        started_at = datetime.combine(session_date, start_time)
        study_session = StudySession(
            daily_log_id=daily_log.id,
            subject_id=subjects[subject_name].id,
            topic="Test topic",
            started_at=started_at,
            ended_at=started_at + timedelta(minutes=duration_minutes),
            duration_minutes=duration_minutes,
            focus_score=focus_score,
        )
        db.add(study_session)
        db.commit()
        db.refresh(study_session)
        return study_session

    return _make
