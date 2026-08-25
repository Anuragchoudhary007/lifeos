from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from config.settings import settings


class UserContextService:
    """Resolves the configured application user for the single-user app.

    This is a temporary application context, not an authentication system.
    It provides one replacement point when authenticated users are introduced.
    """

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_current_user(self) -> User | None:
        return self.repository.get_by_email(
            settings.DEFAULT_USER_EMAIL
        )
