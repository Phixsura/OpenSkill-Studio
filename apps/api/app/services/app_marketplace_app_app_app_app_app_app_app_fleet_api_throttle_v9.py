"""Fleet API Throttle v9 — track API throttling across consumer tiers."""
from __future__ import annotations
def fleet_api_throttle_v9(consumers: list[dict]) -> dict:
    throttled = [c for c in consumers if c.get("throttled")]
    total_requests = sum(c.get("requests_today", 0) for c in consumers)
    throttle_rate = round(len(throttled) / len(consumers) * 100, 1) if consumers else 0
    return {"consumers": len(consumers), "throttled": len(throttled), "total_requests": total_requests,
            "throttle_rate_pct": throttle_rate, "healthy": throttle_rate < 5}
