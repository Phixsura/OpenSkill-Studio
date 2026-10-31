"""Fleet StatusPage.io — track public status page health."""
from __future__ import annotations
def fleet_statuspage_io(pages: list[dict]) -> dict:
    operational = [p for p in pages if p.get("status") == "operational"]
    degraded = [p for p in pages if p.get("status") == "degraded"]
    incidents_active = sum(p.get("active_incidents", 0) for p in pages)
    return {"pages": len(pages), "operational": len(operational), "degraded": len(degraded),
            "active_incidents": incidents_active, "all_green": len(operational) == len(pages)}
