from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models import Subject
from backend.services.subject_service import SubjectService


def test_subject_service_returns_subjects_from_the_service_layer(
    db: Session,
    subjects: dict[str, Subject],
) -> None:
    returned_subjects = SubjectService(db).get_subjects()

    assert [subject.name for subject in returned_subjects] == [
        "Math",
        "Physics",
    ]
