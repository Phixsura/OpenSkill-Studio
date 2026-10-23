"""Webhook log — record and display webhook delivery attempts."""

import secrets
from datetime import datetime, timedelta


def create_delivery_log(*, webhook_id: str, event: str, url: str,
                          status_code: int, response_time_ms: int) -> dict:
    success = 200 <= status_code < 300
    return {
        "delivery_id": f"dlv_{secrets.token_urlsafe(8)}",
        "webhook_id": webhook_id,
        "event": event,
        "url": url,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        "retry_count": 0 if success else 1,
    }


def get_webhook_stats(*, deliveries: list[dict]) -> dict:
    total = len(deliveries)
    successful = sum(1 for d in deliveries if d.get("success"))
    failed = total - successful
    avg_response = round(sum(d.get("response_time_ms", 0) for d in deliveries) / max(total, 1), 1)
    success_rate = round(successful / max(total, 1) * 100, 1)
    by_event: dict[str, int] = {}
    for d in deliveries:
        ev = d.get("event", "unknown")
        by_event[ev] = by_event.get(ev, 0) + 1
    return {
        "total_deliveries": total,
        "successful": successful,
        "failed": failed,
        "success_rate": success_rate,
        "avg_response_ms": avg_response,
        "by_event": by_event,
    }
