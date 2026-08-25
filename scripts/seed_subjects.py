from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.models.subject import Subject
from config.settings import settings


def seed_subjects(db: Session) -> list[Subject]:
    """Create configured default subjects without duplicating existing rows."""
    existing_names = set(db.scalars(select(Subject.name)).all())
    created = [
        Subject(name=name)
        for name in settings.DEFAULT_SUBJECT_NAMES
        if name not in existing_names
    ]

    if created:
        db.add_all(created)
        db.commit()

    return created


def main() -> None:
    db = SessionLocal()
    try:
        created = seed_subjects(db)
        print(f"Seeded {len(created)} subject(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
