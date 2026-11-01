"""Rate limit dashboard — real-time rate limit monitoring across endpoints."""

import html
from datetime import datetime, timezone


def build_rate_limit_dashboard(*, endpoints: list[dict], plan_limit: int = 1000) -> dict:
    items = []
    total_rpm = 0
    throttled = 0
    for ep in endpoints:
        rpm = ep.get("current_rpm", 0)
        limit = ep.get("rpm_limit", plan_limit)
        pct = round(rpm / max(limit, 1) * 100, 1)
        is_throttled = pct >= 100
        if is_throttled:
            throttled += 1
        total_rpm += rpm
        items.append({
            "method": ep.get("method", "GET"),
            "path": html.escape(ep.get("path", "")),
            "current_rpm": rpm, "rpm_limit": limit,
            "usage_pct": pct, "throttled": is_throttled,
        })
    items.sort(key=lambda x: -x["usage_pct"])
    return {"endpoints": items, "total_endpoints": len(items),
            "total_rpm": total_rpm, "throttled_count": throttled,
            "plan_limit": plan_limit,
            "healthy": throttled == 0,
            "checked_at": datetime.now(timezone.utc).isoformat()}
