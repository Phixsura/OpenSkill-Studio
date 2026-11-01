"""Fleet Incident.io — track incident lifecycle management."""
from __future__ import annotations
def fleet_incident_io(incidents: list[dict]) -> dict:
    active = [i for i in incidents if i.get("status") == "active"]
    resolved = [i for i in incidents if i.get("status") == "resolved"]
    avg_ttd = round(sum(i.get("time_to_detect_min", 0) for i in resolved) / max(len(resolved), 1), 1)
    avg_ttr = round(sum(i.get("time_to_resolve_min", 0) for i in resolved) / max(len(resolved), 1), 1)
    return {"total": len(incidents), "active": len(active), "resolved": len(resolved),
            "avg_ttd_min": avg_ttd, "avg_ttr_min": avg_ttr}
