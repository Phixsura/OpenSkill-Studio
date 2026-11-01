"""Gateway observability — unified observability for the API gateway."""
from __future__ import annotations
from collections import defaultdict


def gateway_metrics(requests: list[dict]) -> dict:
    total = len(requests)
    by_status: dict[str, int] = defaultdict(int)
    by_route: dict[str, int] = defaultdict(int)
    total_ms = 0
    errors = 0
    for r in requests:
        bucket = f"{r.get('status', 200) // 100}xx"
        by_status[bucket] += 1
        by_route[r.get("route", "/")] += 1
        total_ms += r.get("latency_ms", 0)
        if r.get("status", 200) >= 500:
            errors += 1
    avg_ms = round(total_ms / max(total, 1), 1)
    error_rate = round(errors / max(total, 1) * 100, 2)
    top_routes = sorted(by_route.items(), key=lambda x: -x[1])[:5]
    return {"total": total, "by_status": dict(by_status), "avg_ms": avg_ms,
            "error_rate_pct": error_rate,
            "top_routes": [{"route": k, "count": v} for k, v in top_routes]}
