"""Fleet API Availability v9 — track multi-region API availability."""
from __future__ import annotations
def fleet_api_availability_v9(regions: list[dict]) -> dict:
    available = [r for r in regions if r.get("available")]
    avg_uptime = sum(r.get("uptime_pct", 0) for r in regions) / len(regions) if regions else 0
    failovers = sum(r.get("failovers_30d", 0) for r in regions)
    return {"regions": len(regions), "available": len(available), "avg_uptime_pct": round(avg_uptime, 3),
            "failovers_30d": failovers, "healthy": len(available) == len(regions)}
