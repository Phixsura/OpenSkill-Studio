"""Fleet AI Status Page — track AI service status."""
from __future__ import annotations
def fleet_ai_status_page(components: list[dict]) -> dict:
    operational = [c for c in components if c.get("status") == "operational"]
    degraded = [c for c in components if c.get("status") == "degraded"]
    outage = [c for c in components if c.get("status") == "outage"]
    overall = "operational" if len(operational) == len(components) else ("degraded" if len(outage) == 0 else "outage")
    return {"components": len(components), "operational": len(operational),
            "degraded": len(degraded), "outage": len(outage), "overall": overall}
