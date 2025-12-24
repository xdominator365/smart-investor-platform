from sqlalchemy import Column, Integer, Boolean, String, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base


class RuleEngineResult(Base):
    __tablename__ = "rule_engine_results"

    id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer, ForeignKey("ml_feature_snapshot.snapshot_id"))

    rule_trend_ok = Column(Boolean)
    rule_rsi_ok = Column(Boolean)
    rule_volume_ok = Column(Boolean)
    rule_volatility_ok = Column(Boolean)

    rules_passed = Column(Boolean)
    risk_level = Column(String)

    blocked_by = Column(JSON)
    explanations = Column(JSON)

    evaluated_at = Column(DateTime, server_default=func.now())
