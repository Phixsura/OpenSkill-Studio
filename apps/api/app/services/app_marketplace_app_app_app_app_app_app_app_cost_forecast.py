"""Cost forecast engine — predict future infrastructure costs."""
from __future__ import annotations
import math


def forecast_costs(monthly_costs: list[float], months_ahead: int = 3) -> dict:
    if len(monthly_costs) < 2:
        return {"forecast": [], "trend": "insufficient_data"}
    avg_growth = sum(monthly_costs[i] - monthly_costs[i-1] for i in range(1, len(monthly_costs))) / (len(monthly_costs) - 1)
    last = monthly_costs[-1]
    forecast = []
    for m in range(1, months_ahead + 1):
        projected = round(last + avg_growth * m, 2)
        forecast.append({"month": m, "projected_cost": max(0, projected),
                          "confidence": round(max(50, 95 - m * 5), 0)})
    total_projected = round(sum(f["projected_cost"] for f in forecast), 2)
    trend = "increasing" if avg_growth > 0 else "decreasing" if avg_growth < 0 else "stable"
    return {"forecast": forecast, "avg_monthly_growth": round(avg_growth, 2),
            "total_projected": total_projected, "trend": trend,
            "current_monthly": last}


def identify_savings(costs_by_service: dict[str, float], threshold_pct: float = 20) -> list[dict]:
    total = sum(costs_by_service.values())
    savings = []
    for svc, cost in sorted(costs_by_service.items(), key=lambda x: -x[1]):
        pct = round(cost / max(total, 0.01) * 100, 1)
        if pct >= threshold_pct:
            savings.append({"service": svc, "cost": cost, "pct_of_total": pct,
                             "recommendation": f"Review {svc} — {pct}% of total spend"})
    return savings
