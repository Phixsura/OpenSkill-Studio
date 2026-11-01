"""Platform API analytics — deep analytics on API usage patterns."""
from __future__ import annotations
from collections import defaultdict


def analyze_endpoints(requests: list[dict]) -> dict:
    by_endpoint: dict[str, dict] = defaultdict(lambda: {"count": 0, "errors": 0, "total_ms": 0})
    by_method: dict[str, int] = defaultdict(int)
    by_status: dict[int, int] = defaultdict(int)
    for r in requests:
        ep = r.get("endpoint", "/")
        by_endpoint[ep]["count"] += 1
        by_endpoint[ep]["total_ms"] += r.get("latency_ms", 0)
        if r.get("status", 200) >= 400:
            by_endpoint[ep]["errors"] += 1
        by_method[r.get("method", "GET")] += 1
        by_status[r.get("status", 200)] += 1
    top_endpoints = sorted(by_endpoint.items(), key=lambda x: -x[1]["count"])[:10]
    slowest = sorted(by_endpoint.items(),
                     key=lambda x: -x[1]["total_ms"] / max(x[1]["count"], 1))[:5]
    return {"total_requests": len(requests), "by_method": dict(by_method),
            "by_status": dict(by_status),
            "top_endpoints": [{"endpoint": k, **v} for k, v in top_endpoints],
            "slowest_endpoints": [{"endpoint": k, "avg_ms": round(v["total_ms"]/max(v["count"],1),1)} for k, v in slowest],
            "unique_endpoints": len(by_endpoint)}


def peak_hours(requests: list[dict]) -> dict:
    by_hour: dict[int, int] = defaultdict(int)
    for r in requests:
        h = r.get("hour", 0)
        by_hour[h] += 1
    peak = max(by_hour.items(), key=lambda x: x[1]) if by_hour else (0, 0)
    return {"by_hour": dict(by_hour), "peak_hour": peak[0], "peak_count": peak[1]}
