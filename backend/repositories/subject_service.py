from sqlalchemy.orm import Session

from backend.repositories.subject_repository import SubjectRepository


class SubjectService:
    def __init__(self, db: Session):
        self.repository = SubjectRepository(db)

    def get_subjects(self):
        return self.repository.get_all()