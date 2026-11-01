"""Fleet AI SRE v8 — track ultimate site reliability engineering."""
from __future__ import annotations
def fleet_ai_sre_v8(teams: list[dict]) -> dict:
    active = [t for t in teams if t.get("active", True)]
    toil = round(sum(t.get("toil_pct", 0) for t in teams) / max(len(teams), 1), 1)
    budget = round(sum(t.get("budget_pct", 0) for t in teams) / max(len(teams), 1), 1)
    slos = sum(t.get("slos", 0) for t in teams)
    return {"teams": len(teams), "active": len(active), "toil": toil,
            "budget": budget, "slos": slos, "elite": toil < 20}
