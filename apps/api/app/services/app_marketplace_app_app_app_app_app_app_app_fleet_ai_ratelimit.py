"""Fleet AI Rate Limiter — track per-user AI API quotas."""
from __future__ import annotations
def fleet_ai_ratelimit(configs: list[dict]) -> dict:
    active = [c for c in configs if c.get("active", True)]
    throttled_24h = sum(c.get("throttled_24h", 0) for c in configs)
    total_requests = sum(c.get("requests_24h", 0) for c in configs)
    return {"configs": len(configs), "active": len(active), "throttled_24h": throttled_24h,
            "requests_24h": total_requests, "effective": throttled_24h < total_requests * 0.05}
