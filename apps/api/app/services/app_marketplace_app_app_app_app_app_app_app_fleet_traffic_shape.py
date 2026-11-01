"""Fleet traffic shaping — track traffic routing weights."""
from __future__ import annotations
def fleet_traffic_shaping(routes: list[dict]) -> dict:
    total_weight = sum(r.get("weight", 0) for r in routes)
    active = [r for r in routes if r.get("weight", 0) > 0]
    return {"routes": len(routes), "active": len(active),
            "total_weight": total_weight, "balanced": all(r.get("weight", 0) == routes[0].get("weight", 0) for r in routes) if routes else True}
