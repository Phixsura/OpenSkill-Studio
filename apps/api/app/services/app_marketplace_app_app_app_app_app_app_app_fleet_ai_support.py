"""Fleet AI Support Ticket — track AI-assisted customer support automation."""
from __future__ import annotations
def fleet_ai_support(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    tickets_24h = sum(s.get("tickets_24h", 0) for s in systems)
    auto_resolved = sum(s.get("auto_resolved", 0) for s in systems)
    avg_resolution_min = round(sum(s.get("resolution_min", 0) for s in systems) / max(len(systems), 1), 1)
    csat = round(sum(s.get("csat", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "tickets_24h": tickets_24h,
            "auto_resolved": auto_resolved, "resolution_min": avg_resolution_min, "csat": csat, "efficient": auto_resolved > 0}
