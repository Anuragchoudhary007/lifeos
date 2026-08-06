"""
Create all database tables.
"""

from backend.database.database import engine
from backend.models import *

from backend.database.base import Base

Base.metadata.create_all(bind=engine)

print("Database created successfully.")