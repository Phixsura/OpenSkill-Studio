"""Fleet cost forecast — project monthly infrastructure costs."""
from __future__ import annotations
def fleet_cost_forecast(daily_cost: float, days_in_month: int = 30) -> dict:
    monthly = round(daily_cost * days_in_month, 2)
    annual = round(monthly * 12, 2)
    return {"daily": daily_cost, "monthly": monthly, "annual": annual,
            "budget_warning": monthly > 50000}
