"""Fleet AI Forecasting — track predictive analytics."""
from __future__ import annotations
def fleet_ai_forecast(models: list[dict]) -> dict:
    active = [m for m in models if m.get("active", True)]
    predictions_24h = sum(m.get("predictions_24h", 0) for m in models)
    mape = round(sum(m.get("mape_pct", 0) for m in models) / max(len(models), 1), 1)
    return {"models": len(models), "active": len(active), "predictions_24h": predictions_24h,
            "mape_pct": mape, "accurate": mape < 10}
