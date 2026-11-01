"""Fleet Cloud Billing v9 — track multi-cloud billing and invoicing."""
from __future__ import annotations
def fleet_cloud_billing_v9(accounts: list[dict]) -> dict:
    total_spend = sum(a.get("monthly_spend", 0) for a in accounts)
    credits = sum(a.get("credits_remaining", 0) for a in accounts)
    forecasted = sum(a.get("forecast", 0) for a in accounts)
    return {"accounts": len(accounts), "monthly_spend": round(total_spend, 2),
            "credits_remaining": round(credits, 2), "forecast": round(forecasted, 2), "healthy": True}
