"""Fleet AI Platform Excellence v7 — track operational excellence at scale."""
from __future__ import annotations
def fleet_ai_platform_excellence_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    uptime = round(sum(s.get("uptime", 0) for s in systems) / max(len(systems), 1), 4)
    incidents_30d = sum(s.get("incidents", 0) for s in systems)
    automations = sum(s.get("automations", 0) for s in systems)
    toil_pct = round(sum(s.get("toil_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "uptime": uptime,
            "incidents": incidents_30d, "automations": automations, "toil_pct": toil_pct, "excellent": uptime > 99.99 and toil_pct < 15}
