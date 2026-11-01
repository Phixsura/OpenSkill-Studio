"""Fleet cost allocation — allocate costs by team/namespace."""
from __future__ import annotations
def fleet_cost_allocation(teams: list[dict]) -> dict:
    total = sum(t.get("cost", 0) for t in teams)
    alloc = {t["team"]: round(t.get("cost", 0) / max(total, 1) * 100, 1) for t in teams if "team" in t}
    top = max(alloc, key=lambda k: alloc[k]) if alloc else None
    return {"total_cost": round(total, 2), "allocation": alloc, "top_spender": top}
