"""Fleet error budget remaining — time-based error budget tracker."""
from __future__ import annotations
def fleet_error_budget_remaining(metrics: dict) -> dict:
    budget_min = metrics.get("budget_minutes", 43.2)  # 99.9% of 30 days
    consumed_min = metrics.get("consumed_minutes", 0)
    remaining = round(max(budget_min - consumed_min, 0), 1)
    pct = round(remaining / max(budget_min, 0.01) * 100, 1)
    return {"budget_min": budget_min, "consumed_min": consumed_min,
            "remaining_min": remaining, "remaining_pct": pct,
            "status": "safe" if pct > 50 else ("warning" if pct > 20 else "critical")}
