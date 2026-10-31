"""Fleet Capacity Forecast v9 — predict future resource needs."""
from __future__ import annotations
def fleet_capacity_forecast_v9(resources: list[dict]) -> dict:
    at_risk = [r for r in resources if r.get("days_to_capacity", 999) < 30]
    avg_growth = sum(r.get("growth_pct_monthly", 0) for r in resources) / len(resources) if resources else 0
    total_cost = sum(r.get("projected_monthly_cost", 0) for r in resources)
    return {"resources": len(resources), "at_risk_30d": len(at_risk),
            "avg_growth_pct": round(avg_growth, 1), "projected_cost": round(total_cost, 2),
            "healthy": len(at_risk) == 0}
