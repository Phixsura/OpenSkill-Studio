"""Fleet API Gateway v9 — track gateway routing and rate limiting."""
from __future__ import annotations
def fleet_api_gateway_v9(routes: list[dict]) -> dict:
    active = [r for r in routes if r.get("active", True)]
    total_rps = sum(r.get("rps", 0) for r in routes)
    throttled = [r for r in routes if r.get("throttled")]
    return {"routes": len(routes), "active": len(active), "total_rps": total_rps,
            "throttled": len(throttled), "healthy": len(throttled) == 0}
