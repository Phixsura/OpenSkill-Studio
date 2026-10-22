"""Webhook log — structured delivery log for developer debugging."""

from datetime import datetime, timezone


def create_log_entry(*, webhook_id: str, event_type: str, url: str,
                       status_code: int, response_time_ms: int, payload_size: int) -> dict:
    success = 200 <= status_code < 300
    return {
        "webhook_id": webhook_id, "event_type": event_type, "url": url,
        "status_code": status_code, "success": success,
        "response_time_ms": response_time_ms, "payload_size": payload_size,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def compute_delivery_stats(*, logs: list[dict]) -> dict:
    if not logs:
        return {"total": 0, "success_rate": 0, "avg_response_ms": 0}
    total = len(logs)
    successes = sum(1 for l in logs if l.get("success"))
    avg_ms = sum(l.get("response_time_ms", 0) for l in logs) / total
    return {
        "total": total, "success_rate": round(successes / total * 100, 1),
        "avg_response_ms": round(avg_ms), "failures": total - successes,
    }
