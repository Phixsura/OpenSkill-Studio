"""Webhook testing sandbox — test webhooks with simulated events."""
from __future__ import annotations
import hashlib
import time
import html


def create_test_event(event_type: str, payload: dict) -> dict:
    event_id = hashlib.sha256(f"{event_type}:{time.time()}".encode()).hexdigest()[:12]
    return {"event_id": event_id, "type": event_type, "payload": payload,
            "created_at": time.time(), "test": True}


def simulate_delivery(event: dict, endpoint: str, timeout_ms: int = 5000) -> dict:
    return {"event_id": event["event_id"], "endpoint": html.escape(endpoint),
            "status_code": 200, "response_ms": 42,
            "delivered": True, "test": True}


def delivery_report(deliveries: list[dict]) -> dict:
    succeeded = sum(1 for d in deliveries if d["delivered"])
    avg_ms = round(sum(d["response_ms"] for d in deliveries) / max(len(deliveries), 1))
    return {"total": len(deliveries), "succeeded": succeeded,
            "failed": len(deliveries) - succeeded, "avg_response_ms": avg_ms,
            "success_rate": round(succeeded / max(len(deliveries), 1) * 100)}
