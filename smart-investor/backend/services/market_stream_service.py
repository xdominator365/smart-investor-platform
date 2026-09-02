import asyncio
import json
import os
import time
import uuid
from typing import Any

from fastapi import WebSocket

from services.market_data_service import MarketDataService

try:
    import redis.asyncio as redis
except Exception:  # pragma: no cover - optional dependency
    redis = None


class MarketStreamService:
    def __init__(self, refresh_interval: int = 15):
        self.refresh_interval = refresh_interval
        self.connections: set[WebSocket] = set()
        self.subscriptions: dict[WebSocket, set[str]] = {}
        self.latest_payloads: dict[str, dict[str, Any]] = {}
        self._client_queues: dict[WebSocket, asyncio.Queue[dict]] = {}
        self._client_sender_tasks: dict[WebSocket, asyncio.Task] = {}
        self._redis_client = None
        self._redis_subscriber_client = None
        self._redis_listener_task = None
        self._instance_id = uuid.uuid4().hex
        self._subscriptions_changed = asyncio.Event()

        if redis is not None:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                self._redis_subscriber_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                )

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        self.subscriptions.setdefault(websocket, set())
        queue = asyncio.Queue(maxsize=100)
        self._client_queues[websocket] = queue
        self._client_sender_tasks[websocket] = asyncio.create_task(
            self._send_client_messages(websocket, queue)
        )

    async def disconnect(self, websocket: WebSocket):
        self.connections.discard(websocket)
        self.subscriptions.pop(websocket, None)
        self._client_queues.pop(websocket, None)
        sender_task = self._client_sender_tasks.pop(websocket, None)
        if sender_task is not None and sender_task is not asyncio.current_task():
            sender_task.cancel()
        self._subscriptions_changed.set()

    async def _send_client_messages(
        self,
        websocket: WebSocket,
        queue: asyncio.Queue[dict],
    ):
        try:
            while True:
                message = await queue.get()
                await asyncio.wait_for(websocket.send_json(message), timeout=5)
        except asyncio.CancelledError:
            raise
        except Exception:
            await self.disconnect(websocket)

    def _queue_message(self, websocket: WebSocket, message: dict):
        queue = self._client_queues.get(websocket)
        if queue is None:
            return
        try:
            queue.put_nowait(message)
        except asyncio.QueueFull:
            try:
                queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                pass

    async def handle_message(self, websocket: WebSocket, message: dict):
        if not isinstance(message, dict):
            return

        message_type = message.get("type", "subscribe")

        if message_type == "ping":
            self._queue_message(websocket, {"type": "pong", "ts": time.time()})
            return

        if message_type in {"subscribe", "symbols"}:
            symbols = message.get("symbols", [])
            if not isinstance(symbols, list):
                return
            await self.subscribe(websocket, symbols)
            return

        if message_type == "unsubscribe":
            symbols = message.get("symbols", [])
            if not isinstance(symbols, list):
                return
            await self.unsubscribe(websocket, symbols)

    async def subscribe(self, websocket: WebSocket, symbols: list[str]):
        normalized = {
            symbol.upper()
            for symbol in symbols
            if isinstance(symbol, str) and symbol.strip()
        }
        self.subscriptions[websocket] = normalized
        self._subscriptions_changed.set()

        self._queue_message(websocket, {
            "type": "connected",
            "symbols": sorted(normalized),
            "ts": time.time(),
        })

        for symbol in sorted(normalized):
            payload = self.latest_payloads.get(symbol)
            if payload:
                self._queue_message(websocket, {
                    "type": "market_update",
                    "symbol": symbol,
                    "data": payload,
                    "ts": time.time(),
                })

    async def unsubscribe(self, websocket: WebSocket, symbols: list[str]):
        existing = self.subscriptions.get(websocket, set())
        to_remove = {
            symbol.upper()
            for symbol in symbols
            if isinstance(symbol, str) and symbol.strip()
        }
        self.subscriptions[websocket] = existing - to_remove
        self._subscriptions_changed.set()

    async def publish(self, message: dict):
        if self._redis_client is not None:
            try:
                await self._redis_client.publish(
                    "market:updates",
                    json.dumps({
                        "origin": self._instance_id,
                        "message": message,
                    }),
                )
            except Exception:
                pass
        await self.broadcast(message)

    async def _listen_redis(self):
        if self._redis_subscriber_client is None:
            return

        pubsub = self._redis_subscriber_client.pubsub()
        await pubsub.subscribe("market:updates")
        try:
            async for event in pubsub.listen():
                if event.get("type") != "message":
                    continue
                envelope = json.loads(event["data"])
                if envelope.get("origin") == self._instance_id:
                    continue
                message = envelope.get("message")
                if isinstance(message, dict):
                    await self.broadcast(message)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - runtime Redis issue
            print(f"[WS] Redis listener stopped: {exc}")
        finally:
            await pubsub.close()

    async def broadcast(self, message: dict):
        for websocket in list(self.connections):
            subscribed = self.subscriptions.get(websocket, set())
            symbol = str(message.get("symbol", "")).upper()
            if symbol and symbol not in subscribed:
                continue
            self._queue_message(websocket, message)

    async def _handle_quote(self, quote: dict):
        symbol = str(quote.get("id", "")).upper()
        price = quote.get("price")
        if not symbol or not isinstance(price, (int, float)) or price <= 0:
            return

        payload = {
            "symbol": symbol,
            "current_price": round(price, 2),
            "open": round(float(quote.get("open_price") or 0), 2),
            "high": round(float(quote.get("day_high") or 0), 2),
            "low": round(float(quote.get("day_low") or 0), 2),
            "volume": int(quote.get("day_volume") or 0),
        }
        if self.latest_payloads.get(symbol) == payload:
            return

        self.latest_payloads[symbol] = payload
        await self.publish({
            "type": "market_update",
            "symbol": symbol,
            "data": payload,
            "ts": time.time(),
            "source_ts": quote.get("time"),
            "source": "yfinance_live_websocket",
            "is_realtime": True,
        })

    def _active_symbols(self) -> set[str]:
        return {
            symbol
            for symbols in self.subscriptions.values()
            for symbol in symbols
        }

    async def _run_yahoo_stream(self):
        from yfinance import AsyncWebSocket

        websocket = AsyncWebSocket(verbose=False)
        listener = None
        try:
            symbols = self._active_symbols()
            if not symbols:
                if not self._subscriptions_changed.is_set():
                    await self._subscriptions_changed.wait()
                self._subscriptions_changed.clear()
                return

            await websocket.subscribe(sorted(symbols))
            listener = asyncio.create_task(websocket.listen(self._handle_quote))

            while True:
                changed = asyncio.create_task(self._subscriptions_changed.wait())
                done, _ = await asyncio.wait(
                    {listener, changed},
                    return_when=asyncio.FIRST_COMPLETED,
                )

                if listener in done:
                    listener.result()
                    return

                changed.cancel()
                self._subscriptions_changed.clear()
                current_symbols = self._active_symbols()
                if not current_symbols:
                    return
                removed_symbols = symbols - current_symbols
                added_symbols = current_symbols - symbols
                if removed_symbols:
                    await websocket.unsubscribe(sorted(removed_symbols))
                if added_symbols:
                    await websocket.subscribe(sorted(added_symbols))
                symbols = current_symbols
        finally:
            if listener is not None:
                listener.cancel()
            await websocket.close()

    async def _poll_once(self, symbols: set[str]):
        async def fetch(symbol: str):
            try:
                return symbol, await asyncio.to_thread(
                    MarketDataService.get_latest_stock_data,
                    symbol,
                    "1m",
                )
            except Exception as exc:  # pragma: no cover - runtime market fetch issue
                print(f"[WS] market refresh failed for {symbol}: {exc}")
                return symbol, None

        results = await asyncio.gather(*(fetch(symbol) for symbol in symbols))
        for symbol, payload in results:
            if payload is None or self.latest_payloads.get(symbol) == payload:
                continue
            self.latest_payloads[symbol] = payload
            await self.publish({
                "type": "market_update",
                "symbol": symbol,
                "data": payload,
                "ts": time.time(),
                "source": "yfinance_history_1m",
                "is_realtime": False,
            })

    async def run(self):
        if self._redis_subscriber_client is not None:
            self._redis_listener_task = asyncio.create_task(self._listen_redis())
        while True:
            try:
                await self._run_yahoo_stream()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # pragma: no cover - runtime provider issue
                print(f"[WS] Yahoo live stream unavailable: {exc}")
                symbols = self._active_symbols()
                if symbols:
                    await self._poll_once(symbols)
                    await asyncio.sleep(self.refresh_interval)

    async def shutdown(self):
        if self._redis_listener_task is not None:
            self._redis_listener_task.cancel()
            await asyncio.gather(self._redis_listener_task, return_exceptions=True)
            self._redis_listener_task = None
        for websocket in list(self.connections):
            await self.disconnect(websocket)
            try:
                await websocket.close()
            except Exception:
                pass
        if self._redis_client is not None:
            await self._redis_client.close()
        if self._redis_subscriber_client is not None:
            await self._redis_subscriber_client.close()
