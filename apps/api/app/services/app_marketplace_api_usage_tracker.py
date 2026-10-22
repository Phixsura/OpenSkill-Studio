"""API usage tracker — rate limit tracking and usage analytics per app."""

from datetime import datetime, timezone
from collections import defaultdict


def track_api_call(*, app_id: str, endpoint: str, method: str, status_code: int,
                     response_time_ms: int, calls: list[dict]) -> list[dict]:
    entry = {
        "app_id": app_id, "endpoint": endpoint, "method": method,
        "status_code": status_code, "response_time_ms": response_time_ms,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return calls + [entry]


def compute_usage_summary(*, calls: list[dict], quota: int = 10000) -> dict:
    total = len(calls)
    by_endpoint = defaultdict(int)
    by_status = defaultdict(int)
    total_ms = 0
    for c in calls:
        by_endpoint[c.get("endpoint", "unknown")] += 1
        by_status[str(c.get("status_code", 0))] += 1
        total_ms += c.get("response_time_ms", 0)
    return {
        "total_calls": total,
        "quota": quota,
        "usage_pct": round(total / max(quota, 1) * 100, 1),
        "remaining": max(0, quota - total),
        "avg_response_ms": round(total_ms / max(total, 1)),
        "by_endpoint": dict(sorted(by_endpoint.items(), key=lambda x: x[1], reverse=True)[:10]),
        "by_status": dict(by_status),
    }


def check_rate_limit(*, app_id: str, window_calls: int, limit: int = 100) -> dict:
    allowed = window_calls < limit
    return {
        "app_id": app_id, "allowed": allowed, "current": window_calls, "limit": limit,
        "remaining": max(0, limit - window_calls),
        "retry_after": None if allowed else 60,
    }
