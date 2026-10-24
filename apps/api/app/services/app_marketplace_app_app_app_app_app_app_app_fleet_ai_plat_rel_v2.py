"""Fleet AI Platform Reliability v2 — track platform reliability engineering."""
from __future__ import annotations
def fleet_ai_platform_reliability_v2(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(len(systems), 1), 3)
    incidents_30d = sum(s.get("incidents_30d", 0) for s in systems)
    mttr_min = round(sum(s.get("mttr_min", 0) for s in systems) / max(len(systems), 1), 1)
    error_budget_remaining = round(sum(s.get("budget_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "uptime": uptime,
            "incidents_30d": incidents_30d, "mttr_min": mttr_min, "budget_pct": error_budget_remaining, "reliable": uptime > 99.9}
