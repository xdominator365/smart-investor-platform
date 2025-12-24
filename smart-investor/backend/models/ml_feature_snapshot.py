from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base


class MLFeatureSnapshot(Base):
    __tablename__ = "ml_feature_snapshot"

    snapshot_id = Column(Integer, primary_key=True)

    symbol = Column(String, index=True)
    snapshot_time = Column(DateTime, server_default=func.now())

    # Market / Price
    price = Column(Float)
    return_1d = Column(Float, nullable=True)
    return_5d = Column(Float, nullable=True)

    # Indicators
    ma20 = Column(Float)
    ma50 = Column(Float)
    rsi_14 = Column(Float)
    rsi_slope = Column(Float)

    # Volume
    volume_ratio = Column(Float)

    # Volatility
    atr_percent = Column(Float)

    # Rule outputs
    rule_trend_ok = Column(Boolean)
    rule_rsi_ok = Column(Boolean)
    rule_volume_ok = Column(Boolean)
    rule_volatility_ok = Column(Boolean)

    rules_passed = Column(Boolean)
    risk_level = Column(String)

    created_at = Column(DateTime, server_default=func.now())