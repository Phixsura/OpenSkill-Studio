"""Webhook Manager — register, verify, and dispatch webhook subscriptions.

Allows extensions and connectors to subscribe to platform events
and receive HTTP callbacks when those events occur.
"""
from __future__ import annotations
import hashlib
import hmac
from datetime import datetime, timezone


_subscriptions: dict[str, dict] = {}
_delivery_log: list[dict] = []


def create_subscription(
    sub_id: str,
    url: str,
    events: list[str],
    owner: str,
    secret: str = "",
) -> dict:
    """Create a new webhook subscription."""
    return _subscriptions.setdefault(sub_id, {
        "sub_id": sub_id,
        "url": url,
        "events": events,
        "owner": owner,
        "secret": secret,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "delivery_count": 0,
        "failure_count": 0,
    })


def get_subscription(sub_id: str) -> dict | None:
    return _subscriptions.get(sub_id)


def list_subscriptions(owner: str | None = None, event: str | None = None) -> list[dict]:
    """List subscriptions filtered by owner and/or event type."""
    subs = [s for s in _subscriptions.values() if s["active"]]
    if owner:
        subs = [s for s in subs if s["owner"] == owner]
    if event:
        subs = [s for s in subs if event in s["events"]]
    return subs


def deactivate_subscription(sub_id: str) -> bool:
    sub = _subscriptions.get(sub_id)
    if sub:
        sub["active"] = False
        return True
    return False


def sign_payload(payload: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for payload verification."""
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def verify_signature(payload: str, secret: str, signature: str) -> bool:
    """Verify an incoming webhook signature."""
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature)


def dispatch_event(event_type: str, payload: dict) -> list[dict]:
    """Find matching subscriptions and simulate delivery."""
    matching = [s for s in _subscriptions.values()
                if s["active"] and event_type in s["events"]]
    deliveries = []
    for sub in matching:
        sub["delivery_count"] += 1
        delivery = {
            "sub_id": sub["sub_id"],
            "url": sub["url"],
            "event_type": event_type,
            "payload_size": len(str(payload)),
            "status": "delivered",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        deliveries.append(delivery)
        _delivery_log.append(delivery)
    return deliveries


def get_delivery_log(sub_id: str | None = None) -> list[dict]:
    if sub_id:
        return [d for d in _delivery_log if d["sub_id"] == sub_id]
    return list(_delivery_log)
