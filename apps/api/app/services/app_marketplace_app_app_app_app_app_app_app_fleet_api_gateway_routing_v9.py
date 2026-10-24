"""Fleet API Gateway Routing v9 — track gateway path-based routing rules."""
from __future__ import annotations
def fleet_api_gateway_routing_v9(routes: list[dict]) -> dict:
    active = [r for r in routes if r.get("active")]
    path_based = [r for r in routes if r.get("type") == "path"]
    header_based = [r for r in routes if r.get("type") == "header"]
    rps = sum(r.get("rps", 0) for r in routes)
    return {"routes": len(routes), "active": len(active), "path_based": len(path_based),
            "header_based": len(header_based), "total_rps": rps, "healthy": len(active) == len(routes)}
