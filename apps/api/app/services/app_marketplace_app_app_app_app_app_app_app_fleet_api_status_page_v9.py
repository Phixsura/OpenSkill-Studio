"""Fleet API Status Page v9 — track public API status page components."""
from __future__ import annotations
def fleet_api_status_page_v9(components: list[dict]) -> dict:
    operational = [c for c in components if c.get("status") == "operational"]
    degraded = [c for c in components if c.get("status") == "degraded"]
    outage = [c for c in components if c.get("status") == "outage"]
    return {"components": len(components), "operational": len(operational),
            "degraded": len(degraded), "outage": len(outage),
            "healthy": len(outage) == 0 and len(degraded) == 0}
