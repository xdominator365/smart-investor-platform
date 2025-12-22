from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)

    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # BUY / SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    realized_pnl = Column(Float, nullable=True)
    strategy = Column(String, default="manual")

    executed_at = Column(DateTime(timezone=True), server_default=func.now())
