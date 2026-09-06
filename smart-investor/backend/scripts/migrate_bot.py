from database import engine
from sqlalchemy import text

def migrate():
    with engine.begin() as conn:
        print("Migrating Portfolio table for Bot Features...")
        
        # Add is_bot_enabled
        try:
            conn.execute(text("ALTER TABLE portfolios ADD COLUMN is_bot_enabled BOOLEAN DEFAULT FALSE"))
            print("Added is_bot_enabled column.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("is_bot_enabled column already exists.")
            else:
                print(f"Error adding is_bot_enabled: {e}")
                
        # Add bot_strategy_id
        try:
            conn.execute(text("ALTER TABLE portfolios ADD COLUMN bot_strategy_id VARCHAR DEFAULT 'trend_follower'"))
            print("Added bot_strategy_id column.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("bot_strategy_id column already exists.")
            else:
                print(f"Error adding bot_strategy_id: {e}")
                
    print("Migration complete!")

if __name__ == "__main__":
    migrate()

