from __future__ import annotations

from sqlalchemy.orm import Session

from backend.repositories.subject_repository import SubjectRepository


class SubjectService:
    """Service for subject operations."""

    def __init__(self, db: Session):
        self.repository = SubjectRepository(db)

    def get_subjects(self):
        return self.repository.get_all()