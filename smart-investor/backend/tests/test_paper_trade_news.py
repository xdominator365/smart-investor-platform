from unittest.mock import MagicMock

import main


def test_manual_buy_includes_news_insights(monkeypatch):
    fake_portfolio = MagicMock(id=12)
    monkeypatch.setattr(main, "get_guest_portfolio", lambda db, x_guest_id=None: fake_portfolio)
    monkeypatch.setattr(
        main.DecisionContextService,
        "build",
        lambda symbol, db=None: {
            "rules": {"rules_passed": True, "blocked_by": []},
            "df": MagicMock(),
            "snapshot": None,
            "features": {"rsi_14": 50, "ma20": 100, "ma50": 90},
        },
    )
    monkeypatch.setattr(main.NewsService, "build_insight", lambda db, symbol: {"sentiment": {"avg_24h": 0.1}})
    monkeypatch.setattr(main.MarketDataService, "get_latest_stock_data", lambda symbol: {"current_price": 100.0})
    monkeypatch.setattr(main.PaperTradeService, "buy", lambda **kwargs: None)

    response = main.paper_buy(symbol="AAPL", quantity=2, x_guest_id="guest-1", db=MagicMock())

    assert "news_insights" in response
    assert response["news_insights"]["sentiment"]["avg_24h"] == 0.1


def test_auto_trade_includes_news_insights(monkeypatch):
    fake_portfolio = MagicMock(id=12)
    fake_position = MagicMock(quantity=0)
    fake_db = MagicMock()
    fake_db.query.return_value.filter_by.return_value.first.return_value = fake_position

    monkeypatch.setattr(main, "get_guest_portfolio", lambda db, x_guest_id=None: fake_portfolio)
    monkeypatch.setattr(main, "is_market_open", lambda: True)
    monkeypatch.setattr(
        main.DecisionContextService,
        "build",
        lambda symbol, db=None: {
            "rules": {"rules_passed": True, "blocked_by": []},
            "df": MagicMock(),
            "snapshot": None,
            "features": {"rsi_14": 50, "ma20": 100, "ma50": 90},
        },
    )
    monkeypatch.setattr(main.NewsService, "build_insight", lambda db, symbol: {"sentiment": {"avg_24h": 0.2}})
    monkeypatch.setattr(main.SignalService, "generate_signal", lambda df, news_insights=None: {"signal": "BUY", "confidence": 80, "reason": "ok", "news_bias": 0.2})
    monkeypatch.setattr(main.MarketDataService, "get_latest_stock_data", lambda symbol: {"current_price": 100.0})
    monkeypatch.setattr(main.PaperTradeService, "buy", lambda **kwargs: None)
    monkeypatch.setattr(main, "AutoTradeDecision", lambda **kwargs: MagicMock())

    response = main.auto_trade(symbol="AAPL", quantity=1, x_guest_id="guest-1", db=fake_db)

    assert "news_insights" in response
    assert response["news_insights"]["sentiment"]["avg_24h"] == 0.2
