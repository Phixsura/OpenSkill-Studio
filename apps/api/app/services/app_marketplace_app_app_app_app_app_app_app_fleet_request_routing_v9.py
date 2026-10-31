"""Fleet Request Routing v9 — track intelligent request routing decisions."""
from __future__ import annotations
def fleet_request_routing_v9(routers: list[dict]) -> dict:
    active = [r for r in routers if r.get("active")]
    weighted = sum(r.get("weighted_routes", 0) for r in routers)
    header_routes = sum(r.get("header_routes", 0) for r in routers)
    return {"routers": len(routers), "active": len(active), "weighted_routes": weighted,
            "header_routes": header_routes, "healthy": len(active) == len(routers)}
