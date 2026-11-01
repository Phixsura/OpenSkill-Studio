"""Fleet AI Time Series — track temporal forecasting and analysis."""
from __future__ import annotations
def fleet_ai_timeseries(models: list[dict]) -> dict:
    active = [m for m in models if m.get("active", True)]
    forecasts_24h = sum(m.get("forecasts_24h", 0) for m in models)
    mape = round(sum(m.get("mape", 0) for m in models) / max(len(models), 1), 2)
    horizon_days = max((m.get("horizon_days", 0) for m in models), default=0)
    return {"models": len(models), "active": len(active), "forecasts_24h": forecasts_24h,
            "mape": mape, "horizon_days": horizon_days, "accurate": mape < 10}
