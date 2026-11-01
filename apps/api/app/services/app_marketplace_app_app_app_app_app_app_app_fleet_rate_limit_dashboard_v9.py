"""Fleet Rate Limit Dashboard v9 — track rate limiting across all APIs."""
from __future__ import annotations
def fleet_rate_limit_dashboard_v9(apis: list[dict]) -> dict:
    total_rps = sum(a.get("rps_limit", 0) for a in apis)
    throttled = sum(a.get("throttled_today", 0) for a in apis)
    consumers_limited = [a for a in apis if a.get("any_consumer_limited")]
    return {"apis": len(apis), "total_rps_capacity": total_rps, "throttled_today": throttled,
            "consumers_limited": len(consumers_limited), "healthy": throttled < 100}
