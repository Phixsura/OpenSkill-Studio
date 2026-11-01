"""Fleet AI Capacity Planner v2 — track AI-driven capacity forecasting."""
from __future__ import annotations
def fleet_ai_capacity_planner_v2(planners: list[dict]) -> dict:
    active = [p for p in planners if p.get("active", True)]
    forecast_days = max((p.get("days", 0) for p in planners), default=0)
    accuracy = round(sum(p.get("accuracy", 0) for p in planners) / max(len(planners), 1), 1)
    savings = round(sum(p.get("savings_pct", 0) for p in planners) / max(len(planners), 1), 1)
    return {"planners": len(planners), "active": len(active), "forecast_days": forecast_days,
            "accuracy": accuracy, "savings_pct": savings, "predictive": accuracy > 85}
