from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime
from zoneinfo import ZoneInfo


def ist_now():
    return datetime.now(ZoneInfo("Asia/Kolkata"))


class NewsEvent(Base):
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    headline = Column(String)
    sentiment_score = Column(Float)
    confidence_score = Column(Float)
    source = Column(String)
    url = Column(String)
    event_time = Column(DateTime)
    ingested_at = Column(DateTime, default=ist_now)
