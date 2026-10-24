"""Gateway rate limit dashboard — aggregate rate limit stats across all routes."""
from __future__ import annotations


def aggregate_rate_limits(routes: list[dict]) -> dict:
    total_requests = 0
    total_blocked = 0
    by_route = []
    for r in routes:
        requests = r.get("requests", 0)
        blocked = r.get("blocked", 0)
        limit = r.get("limit", 0)
        total_requests += requests
        total_blocked += blocked
        usage_pct = round(requests / max(limit, 1) * 100, 1) if limit else 0
        by_route.append({
            "path": r["path"], "method": r.get("method", "ALL"),
            "requests": requests, "blocked": blocked, "limit": limit,
            "usage_pct": usage_pct,
            "status": "exceeded" if blocked > 0 else "warning" if usage_pct > 80 else "ok",
        })
    by_route.sort(key=lambda x: -x["usage_pct"])
    block_rate = round(total_blocked / max(total_requests + total_blocked, 1) * 100, 1)
    return {
        "total_requests": total_requests, "total_blocked": total_blocked,
        "block_rate": block_rate, "block_rate_display": f"{block_rate}%",
        "routes": by_route, "route_count": len(by_route),
        "exceeded_count": sum(1 for r in by_route if r["status"] == "exceeded"),
    }
