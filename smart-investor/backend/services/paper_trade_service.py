from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.portfolio import Portfolio
from models.position import Position
from models.trade import Trade


class PaperTradeService:

    @staticmethod
    def get_portfolio(db: Session, portfolio_id: int):
        portfolio = db.query(Portfolio).get(portfolio_id)
        positions = db.query(Position).filter_by(portfolio_id=portfolio_id).all()
        trades = db.query(Trade).filter_by(portfolio_id=portfolio_id).all()

        realized_pnl = sum(t.realized_pnl or 0 for t in trades)

        # Calculate total holdings value (sum of quantity * avg_price for all positions)
        total_holdings_value = sum((p.quantity or 0) * (p.avg_price or 0) for p in positions)

        return {
            "cash_balance": round(portfolio.cash_balance, 2),
            "holdings": [
                {
                    "symbol": p.symbol,
                    "quantity": p.quantity,
                    "avg_price": p.avg_price
                }
                for p in positions
            ],
            "realized_pnl": round(realized_pnl, 2),
            "total_holdings_value": round(total_holdings_value, 2),
            "trade_history": [
                {
                    "time": t.executed_at,
                    "symbol": t.symbol,
                    "side": t.side,
                    "price": t.price,
                    "quantity": t.quantity,
                    "pnl": t.realized_pnl
                }
                for t in trades
            ]
        }

    @staticmethod
    def buy(db: Session, portfolio_id: int, symbol: str, price: float, quantity: int, strategy="manual"):
        portfolio = db.query(Portfolio).get(portfolio_id)
        
        price = float(price)
        quantity = int(quantity)
        
        cost = price * quantity
        if cost > portfolio.cash_balance:
            raise HTTPException(status_code=400, detail="Insufficient cash")

        position = (
            db.query(Position)
            .filter_by(portfolio_id=portfolio_id, symbol=symbol)
            .first()
        )

        if position:
            total_qty = position.quantity + quantity
            position.avg_price = (
                (position.avg_price * position.quantity + cost) / total_qty
            )
            position.quantity = total_qty
        else:
            position = Position(
                portfolio_id=portfolio_id,
                symbol=symbol,
                quantity=quantity,
                avg_price=price
            )
            db.add(position)

        portfolio.cash_balance -= cost

        trade = Trade(
            portfolio_id=portfolio_id,
            symbol=symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            strategy=strategy
        )

        db.add(trade)
        db.commit()

    @staticmethod
    def sell(db: Session, portfolio_id: int, symbol: str, price: float, quantity: int, strategy="manual"):
        portfolio = db.query(Portfolio).get(portfolio_id)

        position = (
            db.query(Position)
            .filter_by(portfolio_id=portfolio_id, symbol=symbol)
            .first()
        )

        if not position or position.quantity < quantity:
            raise HTTPException(status_code=400, detail="Not enough quantity")
        
        price = float(price)
        quantity = int(quantity)
        pnl = (price - position.avg_price) * quantity

        portfolio.cash_balance += price * quantity
        position.quantity -= quantity

        if position.quantity == 0:
            db.delete(position)

        trade = Trade(
            portfolio_id=portfolio_id,
            symbol=symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            realized_pnl=pnl,
            strategy=strategy
        )

        db.add(trade)
        db.commit()
