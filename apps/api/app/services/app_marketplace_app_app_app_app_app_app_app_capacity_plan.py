"""Capacity planner — forecast resource needs based on growth trends."""
from __future__ import annotations
import math


def forecast_capacity(current_usage: float, growth_rate_pct: float,
                      capacity: float, months_ahead: int = 6) -> dict:
    projections = []
    usage = current_usage
    exhaustion_month = None
    for month in range(1, months_ahead + 1):
        usage = usage * (1 + growth_rate_pct / 100)
        utilization = round(usage / max(capacity, 0.01) * 100, 1)
        projections.append({"month": month, "projected_usage": round(usage, 1),
                            "utilization_pct": utilization})
        if utilization >= 100 and exhaustion_month is None:
            exhaustion_month = month
    return {"current": current_usage, "capacity": capacity,
            "growth_rate_pct": growth_rate_pct,
            "projections": projections,
            "exhaustion_month": exhaustion_month,
            "action_needed": exhaustion_month is not None and exhaustion_month <= 3}


def recommend_scaling(utilization_pct: float, growth_rate_pct: float) -> dict:
    if utilization_pct >= 80 or (utilization_pct >= 60 and growth_rate_pct > 20):
        action = "scale_up_now"
        urgency = "high"
    elif utilization_pct >= 60:
        action = "plan_scaling"
        urgency = "medium"
    else:
        action = "monitor"
        urgency = "low"
    return {"action": action, "urgency": urgency,
            "utilization_pct": utilization_pct, "growth_rate_pct": growth_rate_pct}
