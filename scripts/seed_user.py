from backend.database.session import SessionLocal
from backend.models.user import User
from config.settings import settings


db = SessionLocal()

try:
    user = db.query(User).filter(
        User.email == settings.DEFAULT_USER_EMAIL
    ).first()

    if user is None:
        user = User(
            name=settings.DEFAULT_USER_NAME,
            email=settings.DEFAULT_USER_EMAIL,
            timezone=settings.DEFAULT_USER_TIMEZONE,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"User created: {user.name}")
    else:
        print(f"User already exists: {user.name}")

finally:
    db.close()
