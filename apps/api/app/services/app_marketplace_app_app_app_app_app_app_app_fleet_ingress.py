"""Fleet ingress traffic — aggregate ingress controller metrics."""
from __future__ import annotations
def fleet_ingress_traffic(routes: list[dict]) -> dict:
    total_rps = sum(r.get("rps", 0) for r in routes)
    err_routes = [r for r in routes if r.get("error_rate_pct", 0) > 5]
    return {"total_rps": round(total_rps, 1), "routes": len(routes),
            "error_routes": len(err_routes), "healthy": len(err_routes) == 0}
