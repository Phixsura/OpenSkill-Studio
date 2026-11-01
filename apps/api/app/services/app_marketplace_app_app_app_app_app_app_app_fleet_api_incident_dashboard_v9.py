"""Fleet API Incident Dashboard v9 — unified API incident management."""
from __future__ import annotations
def fleet_api_incident_dashboard_v9(incidents: list[dict]) -> dict:
    open_i = [i for i in incidents if i.get("status") == "open"]
    investigating = [i for i in incidents if i.get("status") == "investigating"]
    resolved = [i for i in incidents if i.get("status") == "resolved"]
    avg_resolution = sum(i.get("resolution_min", 0) for i in resolved) / len(resolved) if resolved else 0
    return {"incidents": len(incidents), "open": len(open_i), "investigating": len(investigating),
            "resolved": len(resolved), "avg_resolution_min": round(avg_resolution, 1), "healthy": len(open_i) == 0}
