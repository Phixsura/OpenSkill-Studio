"""Fleet Incident Manager v9 — track incident lifecycle and resolution."""
from __future__ import annotations
def fleet_incident_mgr_v9(incidents: list[dict]) -> dict:
    open_inc = [i for i in incidents if i.get("status") == "open"]
    resolved = [i for i in incidents if i.get("status") == "resolved"]
    avg_mttr = sum(i.get("mttr_min", 0) for i in resolved) / len(resolved) if resolved else 0
    return {"total": len(incidents), "open": len(open_inc), "resolved": len(resolved),
            "avg_mttr_min": round(avg_mttr, 1), "healthy": len(open_inc) == 0}
