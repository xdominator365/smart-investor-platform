import sys
import os

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime
from database import SessionLocal
from jobs.label_outcomes import run_labeling_job
from utils.market_hours import is_market_open

LOG_FILE = "labeling_job.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} | {msg}\n")
        
def main():
    log("Job started")

    if is_market_open():
        log("Market open, skipping labeling")
        return
    
    db = SessionLocal()
    try:
        run_labeling_job(db, limit=50)
        log("Labeling completed successfully")
    except Exception as e:
        log(f"ERROR: {e}")
    finally:
        db.close()
        log("DB connection closed")

if __name__ == "__main__":
    main()
