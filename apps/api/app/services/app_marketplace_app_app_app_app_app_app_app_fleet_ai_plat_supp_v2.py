"""Fleet AI Platform Support v2 — track enterprise support operations."""
from __future__ import annotations
def fleet_ai_platform_support_v2(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    tickets_24h = sum(s.get("tickets_24h", 0) for s in systems)
    resolution_min = round(sum(s.get("resolution_min", 0) for s in systems) / max(len(systems), 1), 1)
    csat = round(sum(s.get("csat", 0) for s in systems) / max(len(systems), 1), 1)
    sla_met_pct = round(sum(s.get("sla_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "tickets_24h": tickets_24h,
            "resolution_min": resolution_min, "csat": csat, "sla_met": sla_met_pct, "excellent": csat > 4.5}
