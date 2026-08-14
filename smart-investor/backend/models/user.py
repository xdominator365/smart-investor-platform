from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Browser-based anonymous identity for paper trading
    guest_id = Column(String, unique=True, index=True, nullable=True)

    email = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )