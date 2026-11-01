"""API response time tracker — track and alert on response times."""
from __future__ import annotations


def track_response_times(endpoint: str, times_ms: list[float]) -> dict:
    if not times_ms:
        return {"endpoint": endpoint, "count": 0}
    s = sorted(times_ms)
    avg = round(sum(s) / len(s), 1)
    p50 = s[len(s) // 2]
    p99 = s[int(min(len(s) * 0.99, len(s) - 1))]
    slow_count = sum(1 for t in s if t > 500)
    return {"endpoint": endpoint, "count": len(s), "avg_ms": avg,
            "p50_ms": p50, "p99_ms": p99, "min_ms": s[0], "max_ms": s[-1],
            "slow_count": slow_count,
            "slow_pct": round(slow_count / len(s) * 100, 1)}


def compare_endpoints(endpoints: list[dict]) -> dict:
    ranked = sorted(endpoints, key=lambda e: -e.get("p99_ms", 0))
    slowest = ranked[0]["endpoint"] if ranked else None
    fastest = ranked[-1]["endpoint"] if ranked else None
    return {"endpoints": ranked, "slowest": slowest, "fastest": fastest,
            "total_endpoints": len(endpoints)}
