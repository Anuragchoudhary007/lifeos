from datetime import date

from backend.database.session import SessionLocal
from backend.models.daily_log import DailyLog
from backend.models.user import User


db = SessionLocal()

user = db.query(User).filter(User.email == "anurag@lifeos.local").first()

if not user:
    user = User(
        name="Anurag",
        email="anurag@lifeos.local",
        timezone="Asia/Kolkata",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

print(f"User ready: {user.name}")

db.close()