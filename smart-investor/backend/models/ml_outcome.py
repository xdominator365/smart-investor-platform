from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class MLOutcome(Base):
    __tablename__ = "ml_outcomes"

    id = Column(Integer, primary_key=True)

    snapshot_id = Column(Integer, ForeignKey("ml_feature_snapshot.snapshot_id"), index=True)

    horizon_minutes = Column(Integer)   # 15, 30, 60, 1440
    future_return = Column(Float)

    max_favorable_move = Column(Float)
    max_adverse_move = Column(Float)

    outcome_label = Column(String)       # SUCCESS / FAILURE / NEUTRAL
    confidence_score = Column(Float)     # 0–1 (how clean outcome was)

    evaluated_at = Column(DateTime, server_default=func.now())
