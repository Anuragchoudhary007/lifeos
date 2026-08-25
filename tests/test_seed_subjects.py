from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models import Subject
from config.settings import settings
from scripts.seed_subjects import seed_subjects


def test_seed_subjects_is_idempotent(db: Session) -> None:
    first_run = seed_subjects(db)
    second_run = seed_subjects(db)

    assert len(first_run) == len(settings.DEFAULT_SUBJECT_NAMES)
    assert second_run == []
    assert db.scalar(select(func.count()).select_from(Subject)) == len(
        settings.DEFAULT_SUBJECT_NAMES
    )
