"""Fleet AI Capacity Planning — track AI infrastructure scaling forecasts."""
from __future__ import annotations
def fleet_ai_capacity(plans: list[dict]) -> dict:
    active = [p for p in plans if p.get("active", True)]
    forecast_days = max((p.get("forecast_days", 0) for p in plans), default=0)
    utilization = round(sum(p.get("current_util", 0) for p in plans) / max(len(plans), 1), 1)
    headroom_pct = round(100 - utilization, 1)
    return {"plans": len(plans), "active": len(active), "forecast_days": forecast_days,
            "utilization": utilization, "headroom_pct": headroom_pct, "safe": headroom_pct > 20}
