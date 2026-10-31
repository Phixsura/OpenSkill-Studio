"""Fleet AI Incident v3 — track AI-powered incident lifecycle management."""
from __future__ import annotations
def fleet_ai_incident_v3(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    incidents_30d = sum(m.get("incidents_30d", 0) for m in managers)
    p1_count = sum(m.get("p1", 0) for m in managers)
    mttr_min = round(sum(m.get("mttr_min", 0) for m in managers) / max(len(managers), 1), 1)
    postmortems = sum(m.get("postmortems", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "incidents_30d": incidents_30d,
            "p1": p1_count, "mttr_min": mttr_min, "postmortems": postmortems, "learning": postmortems >= p1_count}
