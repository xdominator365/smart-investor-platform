from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class AutoTradeDecision(Base):
    __tablename__ = "auto_trade_decisions"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True, nullable=False)

    signal = Column(String, nullable=False)
    rsi = Column(Float)
    ma20 = Column(Float)
    ma50 = Column(Float)

    action = Column(String, nullable=False)   # EXECUTED / BLOCKED / NO ACTION
    reason = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
