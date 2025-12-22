# Create DB session dependency - This lets your endpoints safely access DB sessions.
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
