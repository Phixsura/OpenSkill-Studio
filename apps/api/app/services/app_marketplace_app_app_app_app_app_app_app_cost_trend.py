"""Service cost trend analyzer — analyze cost trends over time."""
from __future__ import annotations


def analyze_cost_trend(monthly_costs: list[dict]) -> dict:
    if len(monthly_costs) < 2:
        return {"trend": "insufficient_data", "data_points": len(monthly_costs)}
    costs = [m.get("cost", 0) for m in monthly_costs]
    first_half = costs[:len(costs)//2]
    second_half = costs[len(costs)//2:]
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    change_pct = round((avg_second - avg_first) / max(avg_first, 0.01) * 100, 1)
    trend = "increasing" if change_pct > 5 else ("decreasing" if change_pct < -5 else "stable")
    projected_next = round(costs[-1] * (1 + change_pct / 100 / 6), 2)
    return {"trend": trend, "change_pct": change_pct, "current": costs[-1],
            "projected_next": projected_next, "data_points": len(costs),
            "total_spend": round(sum(costs), 2)}
