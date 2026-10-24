"""Fleet AI Usage Forecast — track AI resource demand prediction."""
from __future__ import annotations
def fleet_ai_usage_forecast(forecasters: list[dict]) -> dict:
    active = [f for f in forecasters if f.get("active", True)]
    forecast_days = max((f.get("horizon_days", 0) for f in forecasters), default=0)
    accuracy_pct = round(sum(f.get("accuracy_pct", 0) for f in forecasters) / max(len(forecasters), 1), 1)
    predicted_growth = round(sum(f.get("growth_pct", 0) for f in forecasters) / max(len(forecasters), 1), 1)
    return {"forecasters": len(forecasters), "active": len(active), "horizon_days": forecast_days,
            "accuracy_pct": accuracy_pct, "growth_pct": predicted_growth, "reliable": accuracy_pct > 85}
