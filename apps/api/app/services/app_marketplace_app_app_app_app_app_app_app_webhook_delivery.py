"""Webhook delivery log — track webhook delivery attempts."""
from __future__ import annotations
import html


def record_delivery(endpoint: str, event: str, status_code: int,
                    response_ms: int, payload_bytes: int = 0) -> dict:
    success = 200 <= status_code < 300
    return {"endpoint": html.escape(endpoint), "event": event,
            "status_code": status_code, "response_ms": response_ms,
            "payload_bytes": payload_bytes, "success": success}


def summarize_deliveries(deliveries: list[dict]) -> dict:
    total = len(deliveries)
    successes = sum(1 for d in deliveries if d["success"])
    failures = total - successes
    by_event: dict[str, int] = {}
    avg_ms = 0
    for d in deliveries:
        by_event[d["event"]] = by_event.get(d["event"], 0) + 1
        avg_ms += d["response_ms"]
    avg_ms = round(avg_ms / max(total, 1))
    rate = round(successes / max(total, 1) * 100)
    return {"total": total, "successes": successes, "failures": failures,
            "success_rate": rate, "avg_response_ms": avg_ms,
            "by_event": by_event}
