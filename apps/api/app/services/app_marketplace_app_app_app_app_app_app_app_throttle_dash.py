"""API throttle dashboard — overview of all throttled endpoints."""
from __future__ import annotations


def build_throttle_dashboard(endpoints: list[dict]) -> dict:
    throttled = []
    healthy = 0
    total_blocked = 0
    for ep in endpoints:
        blocked = ep.get("blocked_count", 0)
        total_blocked += blocked
        if blocked > 0:
            throttled.append({"path": ep["path"], "blocked": blocked,
                               "limit": ep.get("limit", 0),
                               "current_rps": ep.get("current_rps", 0)})
        else:
            healthy += 1
    return {"total_endpoints": len(endpoints), "healthy": healthy,
            "throttled_count": len(throttled), "total_blocked": total_blocked,
            "throttled_endpoints": throttled,
            "status": "healthy" if not throttled else "throttling"}
