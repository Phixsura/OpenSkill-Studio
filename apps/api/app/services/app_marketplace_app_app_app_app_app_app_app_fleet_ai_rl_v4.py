"""Fleet AI Rate Limiter v4 — track global adaptive rate limiting."""
from __future__ import annotations
def fleet_ai_rate_limiter_v4(limiters: list[dict]) -> dict:
    active = [l for l in limiters if l.get("active", True)]
    rules = sum(l.get("rules", 0) for l in limiters)
    throttled_24h = sum(l.get("throttled", 0) for l in limiters)
    adaptive = all(l.get("adaptive", False) for l in limiters)
    return {"limiters": len(limiters), "active": len(active), "rules": rules,
            "throttled": throttled_24h, "adaptive": adaptive, "smart": adaptive}
