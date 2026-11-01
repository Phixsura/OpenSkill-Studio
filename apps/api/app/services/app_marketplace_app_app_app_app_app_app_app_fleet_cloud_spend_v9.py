"""Fleet Cloud Spend v9 — track real-time cloud spending by provider."""
from __future__ import annotations
def fleet_cloud_spend_v9(providers: list[dict]) -> dict:
    total_daily = sum(p.get("daily_spend", 0) for p in providers)
    total_monthly = sum(p.get("monthly_forecast", 0) for p in providers)
    over_budget = [p for p in providers if p.get("monthly_forecast", 0) > p.get("budget", float("inf"))]
    return {"providers": len(providers), "daily_spend": round(total_daily, 2),
            "monthly_forecast": round(total_monthly, 2), "over_budget": len(over_budget),
            "healthy": len(over_budget) == 0}
