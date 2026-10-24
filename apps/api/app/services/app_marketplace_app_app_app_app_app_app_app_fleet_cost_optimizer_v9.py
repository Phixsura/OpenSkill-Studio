"""Fleet Cost Optimizer v9 — track cloud cost optimization recommendations."""
from __future__ import annotations
def fleet_cost_optimizer_v9(recommendations: list[dict]) -> dict:
    applied = [r for r in recommendations if r.get("applied")]
    savings = sum(r.get("monthly_savings", 0) for r in recommendations)
    return {"total": len(recommendations), "applied": len(applied),
            "potential_savings": round(savings, 2),
            "applied_savings": round(sum(r.get("monthly_savings", 0) for r in applied), 2),
            "healthy": len(applied) > len(recommendations) * 0.5}
