"""Fleet capacity planning — project resource needs."""
from __future__ import annotations
def fleet_capacity_planning(projections: list[dict]) -> dict:
    needs_expansion = [p for p in projections if p.get("utilization_forecast_pct", 0) > 80]
    total_cost_delta = sum(p.get("cost_delta_usd", 0) for p in needs_expansion)
    return {"total_resources": len(projections), "needs_expansion": len(needs_expansion),
            "cost_delta_usd": round(total_cost_delta, 2), "action_needed": len(needs_expansion) > 0}
