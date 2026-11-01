"""Fleet AI Incident v7 — track ultimate incident lifecycle management."""
from __future__ import annotations
def fleet_ai_incident_v7(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    incidents_30d = sum(m.get("incidents", 0) for m in managers)
    p1 = sum(m.get("p1", 0) for m in managers)
    mttr = round(sum(m.get("mttr_min", 0) for m in managers) / max(len(managers), 1), 1)
    postmortems = sum(m.get("postmortems", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "incidents": incidents_30d,
            "p1": p1, "mttr": mttr, "postmortems": postmortems, "learning": postmortems >= p1}
