"""Fleet AI Cost v5 — track ultimate AI cost management."""
from __future__ import annotations
def fleet_ai_cost_v5(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    total = round(sum(t.get("total_usd", 0) for t in trackers), 2)
    savings = round(sum(t.get("savings_usd", 0) for t in trackers), 2)
    savings_pct = round(savings / max(total + savings, 1) * 100, 1)
    forecast_accuracy = round(sum(t.get("forecast_acc", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "total_usd": total,
            "savings_usd": savings, "savings_pct": savings_pct, "forecast_acc": forecast_accuracy, "optimized": savings_pct > 20}
