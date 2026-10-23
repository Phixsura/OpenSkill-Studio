"""API rate dashboard — real-time rate limit monitoring."""

from datetime import datetime, timezone


def build_rate_dashboard(*, endpoints: list[dict]) -> dict:
    items = []
    total_rpm = 0
    throttled_count = 0
    for ep in endpoints:
        rpm = ep.get("current_rpm", 0)
        limit = ep.get("rpm_limit", 100)
        pct = round(rpm / max(limit, 1) * 100, 1)
        throttled = pct >= 100
        if throttled:
            throttled_count += 1
        total_rpm += rpm
        items.append({"path": ep.get("path", ""), "method": ep.get("method", "GET"),
                       "current_rpm": rpm, "rpm_limit": limit,
                       "usage_pct": pct, "throttled": throttled})
    items.sort(key=lambda x: -x["usage_pct"])
    return {"endpoints": items, "total_endpoints": len(items),
            "total_rpm": total_rpm, "throttled_count": throttled_count,
            "healthy": throttled_count == 0,
            "timestamp": datetime.now(timezone.utc).isoformat()}
