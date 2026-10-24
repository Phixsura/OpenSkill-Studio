"""Fleet Rate Limiter v9 — track API rate limiting and throttling."""
from __future__ import annotations
def fleet_rate_limiter_v9(endpoints: list[dict]) -> dict:
    throttled = sum(e.get("throttled_requests", 0) for e in endpoints)
    total_req = sum(e.get("total_requests", 0) for e in endpoints)
    throttle_pct = round(throttled / total_req * 100, 3) if total_req else 0
    return {"endpoints": len(endpoints), "total_requests": total_req, "throttled": throttled,
            "throttle_pct": throttle_pct, "healthy": throttle_pct < 5}
