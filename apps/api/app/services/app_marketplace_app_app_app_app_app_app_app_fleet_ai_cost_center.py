"""Fleet AI Cost Center — track per-team AI infrastructure cost allocation."""
from __future__ import annotations
def fleet_ai_cost_center(centers: list[dict]) -> dict:
    active = [c for c in centers if c.get("active", True)]
    teams = sum(c.get("teams", 0) for c in centers)
    total_usd = round(sum(c.get("total_usd", 0) for c in centers), 2)
    allocated_pct = round(sum(c.get("allocated_pct", 0) for c in centers) / max(len(centers), 1), 1)
    return {"centers": len(centers), "active": len(active), "teams": teams,
            "total_usd": total_usd, "allocated_pct": allocated_pct, "tracked": allocated_pct > 95}
