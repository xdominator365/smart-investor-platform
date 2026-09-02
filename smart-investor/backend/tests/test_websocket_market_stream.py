from fastapi.testclient import TestClient

import main


def test_market_websocket_accepts_subscription():
    client = TestClient(main.app)

    with client.websocket_connect("/ws/market") as websocket:
        websocket.send_json({"symbols": ["AAPL", "MSFT"]})

        first_message = websocket.receive_json()
        assert first_message["type"] == "connected"
        assert first_message["symbols"] == ["AAPL", "MSFT"]
