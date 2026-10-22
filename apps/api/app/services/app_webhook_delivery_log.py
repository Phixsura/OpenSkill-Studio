"""Webhook delivery log — persistent log of all delivery attempts."""

from collections import defaultdict
from datetime import UTC, datetime

_log: dict[str, list[dict]] = defaultdict(list)


def log_delivery(*, app_id: str, event_type: str, url: str, status_code: int | None,
                 success: bool, duration_ms: int, attempt: int) -> dict:
    entry = {
        "event_type": event_type, "url": url, "status_code": status_code,
        "success": success, "duration_ms": duration_ms, "attempt": attempt,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    _log[app_id].append(entry)
    return entry


def get_delivery_log(app_id: str, *, limit: int = 100) -> list[dict]:
    return _log.get(app_id, [])[-limit:]


def get_failure_log(app_id: str) -> list[dict]:
    return [e for e in _log.get(app_id, []) if not e["success"]]


def get_success_rate(app_id: str) -> float:
    entries = _log.get(app_id, [])
    if not entries:
        return 100.0
    success = sum(1 for e in entries if e["success"])
    return round(success / len(entries) * 100, 1)
