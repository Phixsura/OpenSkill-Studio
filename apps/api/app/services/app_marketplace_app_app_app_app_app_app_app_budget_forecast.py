"""Error budget forecast — project budget exhaustion from current burn rate."""
from __future__ import annotations


def forecast_budget(budget_total: int, consumed: int, daily_burn: float, days_in_period: int = 30) -> dict:
    remaining = max(0, budget_total - consumed)
    pct_consumed = round(consumed / max(budget_total, 1) * 100, 1)
    days_elapsed = round(consumed / max(daily_burn, 0.01))
    days_left = round(remaining / max(daily_burn, 0.01))
    projected_consumption = round(consumed + daily_burn * (days_in_period - min(days_elapsed, days_in_period)))
    will_exhaust = projected_consumption >= budget_total
    return {"budget_total": budget_total, "consumed": consumed, "remaining": remaining,
            "pct_consumed": pct_consumed, "daily_burn": daily_burn,
            "days_until_exhaustion": max(0, days_left),
            "projected_total": projected_consumption, "will_exhaust": will_exhaust}


def recommend_action(forecast: dict) -> dict:
    days = forecast.get("days_until_exhaustion", 999)
    if days <= 3:
        return {"action": "freeze_deploys", "urgency": "critical"}
    elif days <= 7:
        return {"action": "reduce_risk", "urgency": "high"}
    elif forecast.get("will_exhaust"):
        return {"action": "monitor_closely", "urgency": "medium"}
    return {"action": "continue", "urgency": "low"}
