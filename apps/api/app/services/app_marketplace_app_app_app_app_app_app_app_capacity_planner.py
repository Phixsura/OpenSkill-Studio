"""Capacity planner — forecast resource needs based on growth trends."""
from __future__ import annotations
import math


def forecast_capacity(*, current_usage: float, growth_rate_pct: float,
                        capacity: float, unit: str = "GB",
                        months_ahead: int = 12) -> dict:
    projections = []
    usage = current_usage
    exhaustion_month = None
    for m in range(1, months_ahead + 1):
        usage *= (1 + growth_rate_pct / 100)
        pct = round(usage / capacity * 100, 1)
        projections.append({"month": m, "usage": round(usage, 1), "pct": pct,
                            "exceeded": usage > capacity})
        if usage > capacity and exhaustion_month is None:
            exhaustion_month = m
    return {
        "current_usage": current_usage, "capacity": capacity, "unit": unit,
        "growth_rate_pct": growth_rate_pct,
        "current_pct": round(current_usage / capacity * 100, 1),
        "projections": projections,
        "exhaustion_month": exhaustion_month,
        "action_needed": exhaustion_month is not None and exhaustion_month <= 6,
        "recommendation": _recommend(exhaustion_month),
    }


def _recommend(month: int | None) -> str:
    if month is None:
        return "No action needed — capacity sufficient for forecast period"
    if month <= 3:
        return "URGENT: Scale up immediately — capacity exhaustion within 3 months"
    if month <= 6:
        return "Plan capacity upgrade — exhaustion within 6 months"
    return "Monitor growth — exhaustion expected but not imminent"


def estimate_cost(*, current_cost: float, growth_rate_pct: float,
                    months: int = 12) -> dict:
    costs = []
    total = 0.0
    cost = current_cost
    for m in range(1, months + 1):
        cost *= (1 + growth_rate_pct / 100)
        total += cost
        costs.append({"month": m, "cost": round(cost, 2)})
    return {"monthly_costs": costs, "total_cost": round(total, 2),
            "final_monthly": round(cost, 2),
            "total_display": f"${total:,.0f}"}
