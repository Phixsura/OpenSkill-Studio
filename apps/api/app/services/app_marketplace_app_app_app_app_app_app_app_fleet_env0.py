"""Fleet env0 — track environment management and cost."""
from __future__ import annotations
def fleet_env0_status(environments: list[dict]) -> dict:
    active = [e for e in environments if e.get("active", True)]
    cost = sum(e.get("monthly_cost_usd", 0) for e in active)
    ttl_enforced = [e for e in environments if e.get("ttl_enforced", False)]
    return {"total": len(environments), "active": len(active), "monthly_cost": round(cost, 2),
            "ttl_enforced": len(ttl_enforced), "cost_controlled": len(ttl_enforced) == len(environments)}
