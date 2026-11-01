"""Fleet AI Cost Predictor — track AI infrastructure cost forecasting."""
from __future__ import annotations
def fleet_ai_cost_predictor(predictors: list[dict]) -> dict:
    active = [p for p in predictors if p.get("active", True)]
    predictions_24h = sum(p.get("predictions_24h", 0) for p in predictors)
    accuracy_pct = round(sum(p.get("accuracy_pct", 0) for p in predictors) / max(len(predictors), 1), 1)
    savings_found = round(sum(p.get("savings_usd", 0) for p in predictors), 2)
    return {"predictors": len(predictors), "active": len(active), "predictions_24h": predictions_24h,
            "accuracy_pct": accuracy_pct, "savings_usd": savings_found, "valuable": savings_found > 1000}
