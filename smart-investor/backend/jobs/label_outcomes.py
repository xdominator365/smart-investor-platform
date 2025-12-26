'''
NOTE:

What this job does ?

For every ml_feature_snapshot:

Look forward in time (e.g. 60 minutes)
Observe what price actually did
Compare that with the intended decision

Assign:

SUCCESS
FAILURE
NEUTRAL

Store risk-aware metrics

Never touches live trading

This job is offline truth generation.
'''

from datetime import timedelta

from sqlalchemy.orm import Session

from models.ml_feature_snapshot import MLFeatureSnapshot
from models.ml_outcome import MLOutcome
from services.market_data_service import MarketDataService
import pytz
from datetime import datetime, timedelta

IST = pytz.timezone("Asia/Kolkata")


# ================================
# CONFIGURATION (TUNABLE, EXPLICIT)
# ================================

HORIZON_MINUTES = 60          # start with 60 min
SUCCESS_RETURN = 0.007        # +0.7%
FAILURE_RETURN = -0.005       # -0.5%
MAX_ACCEPTABLE_DRAWDOWN = -0.004  # -0.4%


# ================================
# CORE LABELING FUNCTION
# ================================

def label_snapshot(snapshot: MLFeatureSnapshot, db: Session):
    """
    Labels a single feature snapshot based on future price movement.
    """

    # Fetch future market data
    df = MarketDataService.get_historical_data(
        snapshot.symbol,
        period="5d"
    )
    
    snapshot_time = snapshot.snapshot_time

    # ✅ Ensure timezone-aware
    if snapshot_time.tzinfo is None:
        snapshot_time = IST.localize(snapshot_time)
    else:
        snapshot_time = snapshot_time.astimezone(IST)
        
    future_time = snapshot_time + timedelta(minutes=HORIZON_MINUTES)
    
    if df.index.tz is None:
        df.index = df.index.tz_localize(IST)
    else:
        df.index = df.index.tz_convert(IST)
        
    future_df = df[df.index >= future_time]

    # Only consider candles AFTER snapshot time
    future_df = df[df.index > snapshot_time]
    if future_df.empty:
        return None

    # Approximate horizon window (5-min candles assumption)
    candles_needed = HORIZON_MINUTES // 5
    future_df = future_df.head(candles_needed)

    if future_df.empty:
        return None

    # Price metrics
    entry_price = snapshot.price
    final_price = future_df.iloc[-1]["Close"]

    max_price = future_df["High"].max()
    min_price = future_df["Low"].min()

    future_return = (final_price - entry_price) / entry_price
    max_favorable_move = (max_price - entry_price) / entry_price
    max_adverse_move = (min_price - entry_price) / entry_price

    # Infer intent from snapshot
    # (Later this can come from decision logs instead)
    if snapshot.rules_passed:
        intent = "TRADE"
    else:
        intent = "NO_TRADE"

    # Apply labeling logic
    if intent == "TRADE":

        # SUCCESS
        if (
            future_return >= SUCCESS_RETURN and
            max_adverse_move >= MAX_ACCEPTABLE_DRAWDOWN
        ):
            outcome_label = "SUCCESS"

        # FAILURE
        elif future_return <= FAILURE_RETURN:
            outcome_label = "FAILURE"

        # NEUTRAL
        else:
            outcome_label = "NEUTRAL"

    else:  # NO_TRADE intent

        # If market moved strongly, abstaining was a failure
        if abs(future_return) >= SUCCESS_RETURN:
            outcome_label = "FAILURE"
        else:
            outcome_label = "SUCCESS"

    # Confidence score (how clean the outcome was)
    confidence_score = min(abs(future_return) / SUCCESS_RETURN, 1.0)

    # Persist outcome
    outcome = MLOutcome(
    snapshot_id=int(snapshot.snapshot_id),
    horizon_minutes=int(HORIZON_MINUTES),
    future_return=float(future_return),
    max_favorable_move=float(max_favorable_move),
    max_adverse_move=float(max_adverse_move),
    outcome_label=str(outcome_label),
    confidence_score=float(confidence_score)
    )

    db.add(outcome)
    db.commit()

    return outcome_label
    
def run_labeling_job(db, limit=50):
    labeled_count = 0

    try:
        snapshots = (
            db.query(MLFeatureSnapshot)
            .filter(~MLFeatureSnapshot.snapshot_id.in_(
                db.query(MLOutcome.snapshot_id)
            ))
            .order_by(MLFeatureSnapshot.snapshot_time.asc())
            .limit(limit)
            .all()
        )

        for snapshot in snapshots:
            try:
                outcome = label_snapshot(snapshot, db)
                if outcome:
                    db.add(outcome)
                    labeled_count += 1
            except Exception as e:
                db.rollback()
                print(f"[LABELING ERROR] Snapshot {snapshot.snapshot_id}: {e}")

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"[LABELING JOB FAILED] {e}")
        raise

    print(f"[LABELING JOB] Labeled {labeled_count} snapshots")
