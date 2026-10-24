"""Webhook delivery — delivery attempt tracking with response capture."""

import html
import secrets
from datetime import datetime, timezone


def record_delivery(*, webhook_id: str, url: str, event_type: str,
                      status_code: int, response_body: str = "",
                      duration_ms: int = 0) -> dict:
    delivery_id = f"dlv_{secrets.token_hex(8)}"
    success = 200 <= status_code < 300
    return {
        "id": delivery_id, "webhook_id": webhook_id,
        "url": html.escape(url), "event_type": event_type,
        "status_code": status_code, "success": success,
        "response_preview": html.escape(response_body[:200]),
        "duration_ms": duration_ms,
        "delivered_at": datetime.now(timezone.utc).isoformat(),
    }


def build_delivery_stats(*, deliveries: list[dict]) -> dict:
    total = len(deliveries)
    success = sum(1 for d in deliveries if d.get("success"))
    avg_ms = round(sum(d.get("duration_ms", 0) for d in deliveries) / max(total, 1))
    by_event: dict[str, int] = {}
    for d in deliveries:
        et = d.get("event_type", "unknown")
        by_event[et] = by_event.get(et, 0) + 1
    return {"total": total, "success": success, "failed": total - success,
            "success_rate": round(success / max(total, 1) * 100, 1),
            "avg_duration_ms": avg_ms, "by_event": by_event}
