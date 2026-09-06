import pytest
from unittest.mock import MagicMock
from services.paper_trade_service import PaperTradeService
from models.portfolio import Portfolio
from models.position import Position
from models.trade import Trade
from fastapi import HTTPException

def test_buy_successful():
    mock_db = MagicMock()
    mock_portfolio = Portfolio(id=1, cash_balance=10000.0)
    
    def mock_query(model):
        query_mock = MagicMock()
        if model == Portfolio:
            query_mock.get.return_value = mock_portfolio
        elif model == Position:
            query_mock.filter_by.return_value.first.return_value = None
        return query_mock
        
    mock_db.query.side_effect = mock_query
    
    PaperTradeService.buy(
        db=mock_db,
        portfolio_id=1,
        symbol="RELIANCE",
        price=2500.0,
        quantity=2
    )
    
    assert mock_portfolio.cash_balance == 5000.0
    assert mock_db.add.call_count == 2 
    assert mock_db.commit.call_count == 1

def test_buy_insufficient_funds():
    mock_db = MagicMock()
    mock_portfolio = Portfolio(id=1, cash_balance=1000.0)
    
    def mock_query(model):
        query_mock = MagicMock()
        if model == Portfolio:
            query_mock.get.return_value = mock_portfolio
        return query_mock
        
    mock_db.query.side_effect = mock_query
    
    with pytest.raises(HTTPException) as exc:
        PaperTradeService.buy(
            db=mock_db,
            portfolio_id=1,
            symbol="RELIANCE",
            price=2500.0,
            quantity=1
        )
    
    assert exc.value.status_code == 400
    assert "Insufficient cash" in exc.value.detail
    assert mock_db.commit.call_count == 0

def test_sell_successful():
    mock_db = MagicMock()
    mock_portfolio = Portfolio(id=1, cash_balance=5000.0)
    mock_position = Position(portfolio_id=1, symbol="RELIANCE", quantity=5, avg_price=2000.0)
    
    def mock_query(model):
        query_mock = MagicMock()
        if model == Portfolio:
            query_mock.get.return_value = mock_portfolio
        elif model == Position:
            query_mock.filter_by.return_value.first.return_value = mock_position
        return query_mock
        
    mock_db.query.side_effect = mock_query
    
    PaperTradeService.sell(
        db=mock_db,
        portfolio_id=1,
        symbol="RELIANCE",
        price=2500.0,
        quantity=2
    )
    
    assert mock_portfolio.cash_balance == 10000.0
    assert mock_position.quantity == 3
    assert mock_db.add.call_count == 1 
    assert mock_db.commit.call_count == 1

def test_sell_insufficient_quantity():
    mock_db = MagicMock()
    mock_portfolio = Portfolio(id=1, cash_balance=5000.0)
    mock_position = Position(portfolio_id=1, symbol="RELIANCE", quantity=1, avg_price=2000.0)
    
    def mock_query(model):
        query_mock = MagicMock()
        if model == Portfolio:
            query_mock.get.return_value = mock_portfolio
        elif model == Position:
            query_mock.filter_by.return_value.first.return_value = mock_position
        return query_mock
        
    mock_db.query.side_effect = mock_query
    
    with pytest.raises(HTTPException) as exc:
        PaperTradeService.sell(
            db=mock_db,
            portfolio_id=1,
            symbol="RELIANCE",
            price=2500.0,
            quantity=2 
        )
    
    assert exc.value.status_code == 400
    assert "Not enough quantity" in exc.value.detail
    assert mock_db.commit.call_count == 0

