"""Fleet Cost Forecast v9 — track cloud cost forecasting accuracy."""
from __future__ import annotations
def fleet_cost_forecast_v9(forecasts: list[dict]) -> dict:
    accurate = [f for f in forecasts if abs(f.get("variance_pct", 100)) < 10]
    total_forecast = sum(f.get("forecast_amount", 0) for f in forecasts)
    total_actual = sum(f.get("actual_amount", 0) for f in forecasts)
    return {"forecasts": len(forecasts), "accurate": len(accurate),
            "total_forecast": round(total_forecast, 2), "total_actual": round(total_actual, 2),
            "healthy": len(accurate) > len(forecasts) * 0.8}
