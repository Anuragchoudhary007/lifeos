from backend.database.session import SessionLocal


def get_db():
    return SessionLocal()