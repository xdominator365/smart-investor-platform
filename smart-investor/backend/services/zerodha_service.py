import os
import secrets
import time
import math
from urllib.parse import urlencode

from cryptography.fernet import Fernet
from fastapi import HTTPException
from models.broker_account import BrokerAccount
from models.broker_order import BrokerOrder
from models.user import User


class ZerodhaService:
    _pending_states: dict[str, tuple[str, float]] = {}
    _pending_previews: dict[str, tuple[str, dict, float]] = {}
    _state_ttl_seconds = 600

    @staticmethod
    def _api_key() -> str:
        api_key = os.getenv("KITE_API_KEY")
        if not api_key:
            raise RuntimeError("KITE_API_KEY is not configured")
        return api_key

    @staticmethod
    def _frontend_url() -> str:
        return os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

    @staticmethod
    def _fernet() -> Fernet:
        key = os.getenv("BROKER_TOKEN_ENCRYPTION_KEY")
        if not key:
            raise RuntimeError("BROKER_TOKEN_ENCRYPTION_KEY is not configured")
        try:
            return Fernet(key.encode())
        except ValueError as exc:
            raise RuntimeError("BROKER_TOKEN_ENCRYPTION_KEY is invalid") from exc

    @classmethod
    def create_login_url(cls, guest_id: str) -> str:
        state = secrets.token_urlsafe(32)
        cls._pending_states[state] = (
            guest_id,
            time.time() + cls._state_ttl_seconds,
        )
        query = urlencode({"v": "3", "api_key": cls._api_key(), "state": state})
        return f"https://kite.zerodha.com/connect/login?{query}"

    @classmethod
    def complete_login(cls, db, request_token: str, state: str) -> str:
        pending = cls._pending_states.pop(state, None)
        if pending is None or pending[1] < time.time():
            raise ValueError("Zerodha login state is invalid or expired")

        api_secret = os.getenv("KITE_API_SECRET")
        if not api_secret:
            raise RuntimeError("KITE_API_SECRET is not configured")

        from kiteconnect import KiteConnect

        kite = KiteConnect(api_key=cls._api_key())
        session = kite.generate_session(request_token, api_secret=api_secret)
        guest_id = pending[0]
        user = db.query(User).filter(User.guest_id == guest_id).first()
        if user is None:
            raise ValueError("Guest session not found")
        account = db.query(BrokerAccount).filter(BrokerAccount.user_id == user.id).first()
        encrypted_token = cls._fernet().encrypt(session["access_token"].encode()).decode()
        if account is None:
            db.add(BrokerAccount(
                user_id=user.id,
                broker="zerodha",
                broker_user_id=str(session["user_id"]),
                access_token_encrypted=encrypted_token,
            ))
        else:
            account.broker_user_id = str(session["user_id"])
            account.access_token_encrypted = encrypted_token
        db.commit()
        return guest_id

    @classmethod
    def connection_status(cls, db, guest_id: str) -> dict[str, str | bool | None]:
        user = db.query(User).filter(User.guest_id == guest_id).first()
        account = db.query(BrokerAccount).filter(BrokerAccount.user_id == user.id).first() if user else None
        return {
            "connected": account is not None,
            "user_id": account.broker_user_id if account else None,
            "connected_at": account.connected_at.isoformat() if account and account.connected_at else None,
        }

    @classmethod
    def callback_url(cls, status: str, detail: str | None = None) -> str:
        params = {"zerodha": status}
        if detail:
            params["detail"] = detail
        return f"{cls._frontend_url()}/?{urlencode(params)}"

    @classmethod
    def _account(cls, db, guest_id: str) -> BrokerAccount:
        user = db.query(User).filter(User.guest_id == guest_id).first()
        account = db.query(BrokerAccount).filter(BrokerAccount.user_id == user.id).first() if user else None
        if account is None:
            raise HTTPException(status_code=409, detail="Connect Zerodha before placing a live order")
        return account

    @classmethod
    def _kite(cls, db, guest_id: str):
        account = cls._account(db, guest_id)
        from kiteconnect import KiteConnect

        try:
            access_token = cls._fernet().decrypt(account.access_token_encrypted.encode()).decode()
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Stored Zerodha session is invalid") from exc
        kite = KiteConnect(api_key=cls._api_key())
        kite.set_access_token(access_token)
        return kite, account

    @classmethod
    def preview_order(cls, db, guest_id: str, symbol: str, side: str, quantity: int, price: float) -> dict:
        normalized_side = side.upper()
        normalized_symbol = symbol.upper().strip()
        cls._account(db, guest_id)
        if normalized_side not in {"BUY", "SELL"}:
            raise HTTPException(status_code=400, detail="Only BUY or SELL orders can be previewed")
        if quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")
        if not normalized_symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
        if not math.isfinite(price) or price <= 0:
            raise HTTPException(status_code=400, detail="Reference price must be positive")

        zerodha_symbol = normalized_symbol.removesuffix(".NS")
        preview_id = secrets.token_urlsafe(24)
        preview = {
            "preview_id": preview_id,
            "broker": "zerodha",
            "exchange": "NSE",
            "symbol": zerodha_symbol,
            "side": normalized_side,
            "quantity": quantity,
            "order_type": "MARKET",
            "product": "CNC",
            "reference_price": round(float(price), 2),
            "estimated_value": round(float(price) * quantity, 2),
            "live_order_enabled": True,
        }
        cls._pending_previews[preview_id] = (guest_id, preview, time.time() + 300)
        return preview

    @classmethod
    def execute_order(cls, db, guest_id: str, preview_id: str, idempotency_key: str, confirmed: bool) -> dict:
        if not confirmed:
            raise HTTPException(status_code=400, detail="Explicit order confirmation is required")
        if not idempotency_key.strip() or len(idempotency_key) > 128:
            raise HTTPException(status_code=400, detail="A valid idempotency key is required")

        existing = db.query(BrokerOrder).filter(BrokerOrder.idempotency_key == idempotency_key).first()
        if existing is not None:
            return cls._order_response(existing)

        pending = cls._pending_previews.pop(preview_id, None)
        if pending is None or pending[0] != guest_id or pending[2] < time.time():
            raise HTTPException(status_code=409, detail="Order preview is invalid or expired")
        preview = pending[1]
        kite, account = cls._kite(db, guest_id)
        user = db.query(User).filter(User.guest_id == guest_id).first()

        try:
            if preview["side"] == "BUY":
                margins = kite.margins("equity")
                available = float(margins.get("available", {}).get("live_balance", 0))
                if available < preview["estimated_value"]:
                    raise HTTPException(status_code=400, detail="Insufficient Zerodha funds")
            else:
                holdings = kite.holdings()
                holding = next((item for item in holdings if item.get("tradingsymbol") == preview["symbol"] and item.get("exchange") == "NSE"), None)
                if holding is None or int(holding.get("quantity", 0)) < preview["quantity"]:
                    raise HTTPException(status_code=400, detail="Insufficient Zerodha holdings")
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Unable to validate Zerodha funds or holdings") from exc

        audit = BrokerOrder(
            user_id=user.id,
            broker="zerodha",
            idempotency_key=idempotency_key,
            preview_id=preview_id,
            symbol=preview["symbol"],
            exchange=preview["exchange"],
            side=preview["side"],
            quantity=preview["quantity"],
            order_type=preview["order_type"],
            product=preview["product"],
            reference_price=preview["reference_price"],
            estimated_value=preview["estimated_value"],
            status="SUBMITTING",
        )
        db.add(audit)
        db.commit()
        try:
            order_id = kite.place_order(
                variety="regular",
                exchange=preview["exchange"],
                tradingsymbol=preview["symbol"],
                transaction_type=preview["side"],
                quantity=preview["quantity"],
                product=preview["product"],
                order_type=preview["order_type"],
                validity="DAY",
            )
            audit.zerodha_order_id = str(order_id)
            audit.status = "OPEN"
            db.commit()
        except Exception as exc:
            audit.status = "UNKNOWN"
            audit.rejection_reason = str(exc)[:500]
            db.commit()
            raise HTTPException(
                status_code=502,
                detail="Zerodha order status is unknown; check order status before retrying",
            ) from exc
        return cls._order_response(audit)

    @staticmethod
    def _order_response(order: BrokerOrder) -> dict:
        return {
            "order_id": order.id,
            "zerodha_order_id": order.zerodha_order_id,
            "status": order.status,
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "rejection_reason": order.rejection_reason,
            "message": "Order submitted to Zerodha",
        }


    @classmethod
    def order_status(cls, db, guest_id: str, order: BrokerOrder) -> dict:
        if order.zerodha_order_id:
            try:
                kite, _ = cls._kite(db, guest_id)
                history = kite.order_history(order.zerodha_order_id)
                if history:
                    latest = history[-1]
                    order.status = str(latest.get("status", order.status)).upper()
                    order.rejection_reason = latest.get("status_message") or order.rejection_reason
                    db.commit()
            except Exception:
                pass
        return cls._order_response(order)