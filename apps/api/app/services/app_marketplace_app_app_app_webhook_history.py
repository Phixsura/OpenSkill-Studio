"""App webhook history — complete webhook delivery history."""

import html
from collections import defaultdict
from datetime import datetime, timezone


def build_webhook_history(*, deliveries: list[dict], period: str = "24h") -> dict:
    by_status: dict[str, int] = defaultdict(int)
    by_event: dict[str, int] = defaultdict(int)
    total_ms = 0
    for d in deliveries:
        status = "success" if 200 <= d.get("status_code", 0) < 300 else "failed"
        by_status[status] += 1
        by_event[d.get("event_type", "unknown")] += 1
        total_ms += d.get("duration_ms", 0)
    success = by_status.get("success", 0)
    failed = by_status.get("failed", 0)
    total = success + failed
    return {
        "period": period, "total": total, "success": success, "failed": failed,
        "success_rate": round(success / max(total, 1) * 100, 1),
        "avg_duration_ms": round(total_ms / max(total, 1)),
        "by_event": dict(by_event),
        "top_event": max(by_event, key=by_event.get) if by_event else None,
    }
