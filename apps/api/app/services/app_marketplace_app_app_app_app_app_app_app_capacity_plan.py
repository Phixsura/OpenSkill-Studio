"""Capacity planner — forecast resource needs based on growth."""
from __future__ import annotations
import math


def forecast_capacity(current_usage: float, growth_rate_pct: float,
                       months: int = 12, capacity_limit: float = 100) -> dict:
    projections = []
    usage = current_usage
    months_to_limit = None
    for m in range(1, months + 1):
        usage = usage * (1 + growth_rate_pct / 100)
        pct = round(usage / capacity_limit * 100, 1)
        projections.append({"month": m, "usage": round(usage, 1), "pct_of_capacity": pct})
        if pct >= 100 and months_to_limit is None:
            months_to_limit = m
    return {"current": current_usage, "growth_rate": growth_rate_pct,
            "projections": projections, "final_usage": round(usage, 1),
            "months_to_limit": months_to_limit,
            "needs_expansion": months_to_limit is not None and months_to_limit <= 6}


def recommend_scaling(forecast: dict) -> dict:
    if forecast["needs_expansion"]:
        factor = math.ceil(forecast["final_usage"] / 100)
        return {"action": "scale_up", "recommended_capacity": factor * 100,
                "urgency": "high" if forecast["months_to_limit"] and forecast["months_to_limit"] <= 3 else "medium"}
    return {"action": "monitor", "recommended_capacity": 100, "urgency": "low"}
