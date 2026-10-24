"""Fleet cost trend — track monthly infra cost trajectory."""
from __future__ import annotations
def fleet_cost_trend(months: list[dict]) -> dict:
    costs = [m.get("cost", 0) for m in months]
    if len(costs) < 2:
        return {"trend": "stable", "months": len(costs), "latest": costs[-1] if costs else 0}
    change = round((costs[-1] - costs[-2]) / max(costs[-2], 0.01) * 100, 1)
    trend = "increasing" if change > 5 else ("decreasing" if change < -5 else "stable")
    return {"trend": trend, "change_pct": change, "latest": costs[-1], "months": len(costs)}
