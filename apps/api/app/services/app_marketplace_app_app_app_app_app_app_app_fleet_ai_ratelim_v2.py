"""Fleet AI Rate Limiter v2 — track adaptive per-user AI rate limiting."""
from __future__ import annotations
def fleet_ai_rate_limiter_v2(limiters: list[dict]) -> dict:
    active = [l for l in limiters if l.get("active", True)]
    throttled_24h = sum(l.get("throttled_24h", 0) for l in limiters)
    total_requests = sum(l.get("total_24h", 0) for l in limiters)
    throttle_pct = round(throttled_24h / max(total_requests, 1) * 100, 2)
    return {"limiters": len(limiters), "active": len(active), "throttled_24h": throttled_24h,
            "total_24h": total_requests, "throttle_pct": throttle_pct, "fair": throttle_pct < 5}
