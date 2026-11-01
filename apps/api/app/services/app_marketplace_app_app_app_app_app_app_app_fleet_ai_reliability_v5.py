"""Fleet AI Reliability v5 — track ultimate platform reliability engineering."""
from __future__ import annotations
def fleet_ai_reliability_v5(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(len(systems), 1), 4)
    mttr_min = round(sum(s.get("mttr_min", 0) for s in systems) / max(len(systems), 1), 1)
    error_budget = round(sum(s.get("budget_pct", 0) for s in systems) / max(len(systems), 1), 1)
    slis = sum(s.get("slis", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "uptime": uptime,
            "mttr_min": mttr_min, "budget_pct": error_budget, "slis": slis, "five_nines": uptime >= 99.999}
