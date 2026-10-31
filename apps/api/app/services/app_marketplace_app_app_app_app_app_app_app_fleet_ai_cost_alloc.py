"""Fleet AI Cost Allocation — track per-team AI infrastructure cost breakdown."""
from __future__ import annotations
def fleet_ai_cost_allocation(allocators: list[dict]) -> dict:
    active = [a for a in allocators if a.get("active", True)]
    teams = sum(a.get("teams", 0) for a in allocators)
    total_cost = round(sum(a.get("total_usd", 0) for a in allocators), 2)
    allocated_pct = round(sum(a.get("allocated_pct", 0) for a in allocators) / max(len(allocators), 1), 1)
    return {"allocators": len(allocators), "active": len(active), "teams": teams,
            "total_usd": total_cost, "allocated_pct": allocated_pct, "tracked": allocated_pct > 90}
