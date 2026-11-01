"""Cost per service trend — track cost changes per service."""
from __future__ import annotations
def cost_trend(months: list[dict]) -> dict:
    if len(months) < 2: return {"trend": "stable"}
    costs = [m.get("cost", 0) for m in months]
    change = round((costs[-1] - costs[0]) / max(costs[0], 0.01) * 100, 1)
    trend = "increasing" if change > 10 else ("decreasing" if change < -10 else "stable")
    return {"trend": trend, "change_pct": change, "current": costs[-1], "initial": costs[0]}
