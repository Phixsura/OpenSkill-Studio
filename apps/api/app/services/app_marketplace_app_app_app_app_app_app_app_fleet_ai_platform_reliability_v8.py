"""Fleet AI Reliability v8 — track ultimate five-nines reliability."""
from __future__ import annotations
def fleet_ai_reliability_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    uptime = round(sum(s.get("uptime_pct", 0) for s in systems) / max(len(systems), 1), 4)
    mttr = round(sum(s.get("mttr_min", 0) for s in systems) / max(len(systems), 1), 1)
    budget = round(sum(s.get("budget_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "uptime": uptime,
            "mttr": mttr, "budget": budget, "five_nines": uptime >= 99.999}
