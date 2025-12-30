import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:290999@127.0.0.1:5432/smart_investor"

engine = create_engine(DB_URL)

query = """
SELECT
    s.snapshot_id,
    s.price,
    s.ma20,
    s.ma50,
    s.rsi_14,
    s.rsi_slope,
    s.volume_ratio,
    s.atr_percent,
    s.rule_trend_ok,
    s.rule_rsi_ok,
    s.rule_volume_ok,
    s.rule_volatility_ok,
    o.outcome_label,
    o.confidence_score
FROM ml_feature_snapshot s
JOIN ml_outcomes o
  ON s.snapshot_id = o.snapshot_id
"""
# THIS CONDITION COMMENTED OUT TO EXPORT ALL DATA FOR NOW AS WE DONT HAVE MUCH
# # WHERE
#   s.rules_passed = TRUE
#   AND o.horizon_minutes = 60

df = pd.read_sql(query, engine)

df.to_csv("ml_training_data.csv", index=False)

print("Exported:", df.shape)
