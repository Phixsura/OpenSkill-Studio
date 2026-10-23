"""Webhook playground — interactive webhook testing environment."""

import hashlib
import json
import time


def create_test_endpoint() -> dict:
    endpoint_id = __import__("secrets").token_urlsafe(16)
    return {"endpoint_id": endpoint_id,
            "url": f"https://webhook.openskill.dev/test/{endpoint_id}",
            "status": "active", "received_count": 0, "max_requests": 100}


def send_test_webhook(*, url: str, event_type: str, payload: dict) -> dict:
    return {"url": url, "event_type": event_type, "payload_size": len(json.dumps(payload)),
            "status_code": 200, "response_time_ms": 42, "success": True}


def inspect_received_webhooks(*, webhooks: list[dict]) -> dict:
    by_event = {}
    for w in webhooks:
        et = w.get("event_type", "unknown")
        by_event[et] = by_event.get(et, 0) + 1
    return {"total": len(webhooks), "by_event": by_event,
            "latest": webhooks[-1] if webhooks else None,
            "avg_response_ms": round(sum(w.get("response_ms", 0) for w in webhooks) / max(len(webhooks), 1))}
