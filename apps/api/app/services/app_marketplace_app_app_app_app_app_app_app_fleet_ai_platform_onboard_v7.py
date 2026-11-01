"""Fleet AI Onboarding v7 — track developer onboarding optimization."""
from __future__ import annotations
def fleet_ai_onboarding_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    completions = sum(s.get("completions_30d", 0) for s in systems)
    ttfv_min = round(sum(s.get("ttfv_min", 0) for s in systems) / max(len(systems), 1), 1)
    drop_off = round(sum(s.get("drop_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "completions": completions,
            "ttfv_min": ttfv_min, "drop_pct": drop_off, "smooth": drop_off < 20}
