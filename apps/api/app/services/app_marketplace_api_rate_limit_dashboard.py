"""API rate limit dashboard — display current rate limit status per endpoint."""


def get_rate_limit_status(*, endpoints: list[dict]) -> dict:
    results = []
    for ep in endpoints:
        limit = ep.get("limit", 1000)
        used = ep.get("used", 0)
        remaining = max(limit - used, 0)
        pct = round(used / max(limit, 1) * 100, 1)
        results.append({
            "endpoint": ep["path"],
            "method": ep.get("method", "GET"),
            "limit": limit,
            "used": used,
            "remaining": remaining,
            "usage_pct": pct,
            "throttled": pct >= 100,
            "warning": 80 <= pct < 100,
            "reset_in_sec": ep.get("reset_in_sec", 60),
        })
    throttled = [r for r in results if r["throttled"]]
    return {
        "endpoints": results,
        "total_endpoints": len(results),
        "throttled_count": len(throttled),
        "overall_health": "critical" if throttled else "healthy",
    }
