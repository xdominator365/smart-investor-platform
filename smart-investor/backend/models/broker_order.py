from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.sql import func

from database import Base


class BrokerOrder(Base):
    __tablename__ = "broker_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    broker = Column(String, nullable=False, default="zerodha")
    idempotency_key = Column(String, nullable=False, unique=True, index=True)
    preview_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False, default="NSE")
    side = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False, default="MARKET")
    product = Column(String, nullable=False, default="CNC")
    reference_price = Column(Float, nullable=False)
    estimated_value = Column(Float, nullable=False)
    zerodha_order_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="SUBMITTING")
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
