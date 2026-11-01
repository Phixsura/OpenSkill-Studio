"""Fleet API Consumer v9 — track API consumer registration and usage."""
from __future__ import annotations
def fleet_api_consumer_v9(consumers: list[dict]) -> dict:
    active = [c for c in consumers if c.get("active")]
    calls = sum(c.get("calls_today", 0) for c in consumers)
    plans = len({c.get("plan") for c in consumers if c.get("plan")})
    return {"consumers": len(consumers), "active": len(active), "calls_today": calls,
            "unique_plans": plans, "healthy": True}
