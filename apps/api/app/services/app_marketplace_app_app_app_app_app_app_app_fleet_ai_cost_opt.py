"""Fleet AI Cost Optimizer — track AI infrastructure cost optimization."""
from __future__ import annotations
def fleet_ai_cost_optimizer(optimizers: list[dict]) -> dict:
    active = [o for o in optimizers if o.get("active", True)]
    monthly_spend = round(sum(o.get("monthly_spend", 0) for o in optimizers), 2)
    savings = round(sum(o.get("savings", 0) for o in optimizers), 2)
    savings_pct = round(savings / max(monthly_spend + savings, 1) * 100, 1)
    return {"optimizers": len(optimizers), "active": len(active), "monthly_spend": monthly_spend,
            "savings": savings, "savings_pct": savings_pct, "optimized": savings_pct > 20}
