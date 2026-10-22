"""Error tracking — aggregate and classify app runtime errors."""

from collections import defaultdict


def classify_error(*, status_code: int, message: str) -> dict:
    if status_code >= 500:
        category = "server_error"
        severity = "critical" if status_code == 503 else "high"
    elif status_code == 429:
        category = "rate_limit"
        severity = "medium"
    elif status_code >= 400:
        category = "client_error"
        severity = "low"
    else:
        category = "unknown"
        severity = "low"
    return {"category": category, "severity": severity, "status_code": status_code}


def aggregate_errors(*, errors: list[dict]) -> dict:
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    for e in errors:
        by_category[e.get("category", "unknown")] += 1
        by_status[str(e.get("status_code", 0))] += 1
    return {
        "total": len(errors),
        "by_category": dict(by_category),
        "by_status": dict(sorted(by_status.items(), key=lambda x: -x[1])),
        "critical_count": sum(1 for e in errors if e.get("severity") == "critical"),
    }


def build_error_trend(*, hourly_counts: list[dict]) -> dict:
    if not hourly_counts:
        return {"trend": "stable", "avg": 0, "peak": 0}
    values = [h.get("count", 0) for h in hourly_counts]
    avg = sum(values) / len(values)
    peak = max(values)
    recent = values[-3:] if len(values) >= 3 else values
    recent_avg = sum(recent) / len(recent)
    trend = "rising" if recent_avg > avg * 1.5 else "falling" if recent_avg < avg * 0.5 else "stable"
    return {"trend": trend, "avg": round(avg, 1), "peak": peak}
