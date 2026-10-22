"""Webhook delivery tracker — track delivery attempts and outcomes."""

from collections import defaultdict
from datetime import UTC, datetime

_deliveries: dict[str, list[dict]] = defaultdict(list)


def track_attempt(*, delivery_id: str, app_id: str, attempt: int, status_code: int | None, duration_ms: int, success: bool) -> dict:
    entry = {
        "attempt": attempt, "status_code": status_code, "duration_ms": duration_ms,
        "success": success, "timestamp": datetime.now(UTC).isoformat(),
    }
    _deliveries[delivery_id].append(entry)
    return entry


def get_delivery_attempts(delivery_id: str) -> list[dict]:
    return _deliveries.get(delivery_id, [])


def get_delivery_outcome(delivery_id: str) -> str:
    attempts = _deliveries.get(delivery_id, [])
    if not attempts:
        return "pending"
    if any(a["success"] for a in attempts):
        return "delivered"
    return "failed"


def clear_tracker() -> int:
    count = sum(len(v) for v in _deliveries.values())
    _deliveries.clear()
    return count
