from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.subject import Subject


class SubjectRepository:
    """Repository for subject operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Subject]:
        stmt = select(Subject).order_by(Subject.name)
        return list(self.db.scalars(stmt).all())