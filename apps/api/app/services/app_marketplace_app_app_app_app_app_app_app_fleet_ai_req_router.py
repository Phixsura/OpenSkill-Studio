"""Fleet AI Request Router — track intelligent request routing decisions."""
from __future__ import annotations
def fleet_ai_request_router(routers: list[dict]) -> dict:
    active = [r for r in routers if r.get("active", True)]
    routes_24h = sum(r.get("routes_24h", 0) for r in routers)
    strategies = set()
    for r in routers:
        strategies.update(r.get("strategies", []))
    optimal_pct = round(sum(r.get("optimal_pct", 0) for r in routers) / max(len(routers), 1), 1)
    return {"routers": len(routers), "active": len(active), "routes_24h": routes_24h,
            "strategies": sorted(strategies), "optimal_pct": optimal_pct, "smart": optimal_pct > 90}
