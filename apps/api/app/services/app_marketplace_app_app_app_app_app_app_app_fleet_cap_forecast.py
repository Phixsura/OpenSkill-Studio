"""Fleet capacity forecast — predict when resources will be exhausted."""
from __future__ import annotations
def fleet_capacity_forecast(current_pct: float, growth_pct_per_day: float) -> dict:
    if growth_pct_per_day <= 0:
        return {"days_until_full": -1, "urgent": False, "current_pct": current_pct}
    remaining = 100 - current_pct
    days = round(remaining / growth_pct_per_day, 1)
    return {"days_until_full": days, "urgent": days < 30, "current_pct": current_pct}
