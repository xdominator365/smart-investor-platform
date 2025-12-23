from datetime import datetime, time
import pytz

IST = pytz.timezone("Asia/Kolkata")

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)

def is_market_open(now: datetime | None = None) -> bool:
    if not now:
        now = datetime.now(IST)

    current_time = now.time()

    # Monday = 0, Sunday = 6
    if now.weekday() >= 5:
        return False

    return MARKET_OPEN <= current_time <= MARKET_CLOSE
