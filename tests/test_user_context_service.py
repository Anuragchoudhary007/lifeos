from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from backend.models import User
from backend.services.user_context_service import UserContextService
from config.settings import settings


def test_configured_single_user_defaults_are_centralized() -> None:
    assert settings.DEFAULT_USER_NAME == "Anurag"
    assert settings.DEFAULT_USER_EMAIL == "anurag@lifeos.local"
    assert settings.DEFAULT_USER_TIMEZONE == "Asia/Kolkata"
    assert settings.DEFAULT_WEEKLY_STUDY_GOAL_HOURS == 20.0


def test_current_user_resolution_uses_configured_email(
    db: Session,
    monkeypatch,
) -> None:
    configured_email = "configured-user@lifeos.local"
    configured_user = User(
        name="Configured User",
        email=configured_email,
    )
    db.add(configured_user)
    db.commit()
    monkeypatch.setattr(settings, "DEFAULT_USER_EMAIL", configured_email)

    resolved_user = UserContextService(db).get_current_user()

    assert resolved_user is not None
    assert resolved_user.id == configured_user.id


def test_current_user_resolution_returns_none_when_user_is_missing(
    db: Session,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "DEFAULT_USER_EMAIL",
        "missing-user@lifeos.local",
    )

    assert UserContextService(db).get_current_user() is None


def test_study_page_uses_user_context_instead_of_a_hardcoded_email() -> None:
    page_source = Path("pages/01_Study.py").read_text(encoding="utf-8")

    assert "UserContextService" in page_source
    assert "anurag@lifeos.local" not in page_source
