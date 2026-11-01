"""Fleet churn rate — track developer platform churn."""
from __future__ import annotations
def fleet_churn_rate(metrics: dict) -> dict:
    start = metrics.get("start_users", 0)
    end = metrics.get("end_users", 0)
    new = metrics.get("new_users", 0)
    churned = start + new - end
    rate = round(churned / max(start, 1) * 100, 1)
    return {"churned": max(churned, 0), "churn_rate_pct": max(rate, 0),
            "net_growth": end - start, "healthy": rate < 5}
