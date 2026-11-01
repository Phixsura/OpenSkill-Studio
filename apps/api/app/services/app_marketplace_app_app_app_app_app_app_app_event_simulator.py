"""Webhook event simulator — generate and send test events for development."""
from __future__ import annotations
import secrets
import time


TEMPLATES = {
    "app.installed": {"app_id": "app_test", "user_id": "user_test", "plan": "free"},
    "app.uninstalled": {"app_id": "app_test", "user_id": "user_test"},
    "user.created": {"user_id": "user_test", "email": "test@example.com"},
    "payment.completed": {"payment_id": "pay_test", "amount": 29.99, "currency": "USD"},
    "deploy.completed": {"app_id": "app_test", "version": "1.0.0", "status": "success"},
}


def list_templates() -> list[dict]:
    return [{"event_type": k, "fields": list(v.keys())} for k, v in TEMPLATES.items()]


def generate_event(event_type: str, *, overrides: dict | None = None) -> dict:
    template = TEMPLATES.get(event_type)
    if not template:
        return {"error": f"Unknown event type: {event_type}"}
    payload = {**template, **(overrides or {})}
    return {
        "id": f"evt_{secrets.token_hex(8)}",
        "type": event_type,
        "payload": payload,
        "timestamp": int(time.time()),
        "test": True,
    }


def simulate_delivery(event: dict, *, url: str, status_code: int = 200,
                       latency_ms: int = 150) -> dict:
    return {
        "event_id": event.get("id", ""),
        "url": url, "status_code": status_code,
        "latency_ms": latency_ms,
        "success": 200 <= status_code < 300,
        "test": True,
    }
