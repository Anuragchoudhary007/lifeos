from backend.database.session import SessionLocal
from backend.models.user import User


db = SessionLocal()

try:
    user = db.query(User).filter(
        User.email == "anurag@lifeos.local"
    ).first()

    if user is None:
        user = User(
            name="Anurag",
            email="anurag@lifeos.local",
            timezone="Asia/Kolkata",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"User created: {user.name}")
    else:
        print(f"User already exists: {user.name}")

finally:
    db.close()