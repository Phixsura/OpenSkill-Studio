"""Fleet Global Load Balancer v9 — track global traffic distribution."""
from __future__ import annotations
def fleet_global_lb_v9(regions: list[dict]) -> dict:
    active = [r for r in regions if r.get("active")]
    rps = sum(r.get("rps", 0) for r in regions)
    failovers = sum(r.get("failovers_today", 0) for r in regions)
    return {"regions": len(regions), "active": len(active), "total_rps": rps,
            "failovers_today": failovers, "healthy": len(active) == len(regions)}
