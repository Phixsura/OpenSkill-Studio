"""Fleet AI Onboarding Wizard — track developer onboarding automation."""
from __future__ import annotations
def fleet_ai_onboarding(wizards: list[dict]) -> dict:
    active = [w for w in wizards if w.get("active", True)]
    completions_24h = sum(w.get("completions_24h", 0) for w in wizards)
    avg_time_min = round(sum(w.get("avg_min", 0) for w in wizards) / max(len(wizards), 1), 1)
    drop_off_pct = round(sum(w.get("drop_off_pct", 0) for w in wizards) / max(len(wizards), 1), 1)
    return {"wizards": len(wizards), "active": len(active), "completions_24h": completions_24h,
            "avg_min": avg_time_min, "drop_off_pct": drop_off_pct, "smooth": drop_off_pct < 20}
