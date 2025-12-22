from database import SessionLocal
from models.user import User
from models.portfolio import Portfolio

db = SessionLocal()

user = db.query(User).first()

if not user:
    user = User(email="harshit@smartinvestor.com", name="Harshit Yadav")
    db.add(user)
    db.commit()
    db.refresh(user)

portfolio = db.query(Portfolio).filter_by(user_id=user.id).first()

if not portfolio:
    portfolio = Portfolio(
        user_id=user.id,
        name="Paper Portfolio",
        cash_balance=100000.0
    )
    db.add(portfolio)
    db.commit()

db.close()
print("✅ Seed completed")
