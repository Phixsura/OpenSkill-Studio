"""Service availability predictor — predict future availability from trends."""
from __future__ import annotations


def predict_availability(history: list[float], forecast_days: int = 7) -> dict:
    if len(history) < 3:
        return {"forecast": [], "trend": "insufficient_data"}
    n = len(history)
    recent = sum(history[-3:]) / 3
    older = sum(history[:3]) / 3
    slope = (recent - older) / max(n, 1)
    forecast = []
    current = history[-1]
    for d in range(1, forecast_days + 1):
        projected = max(0, min(100, current + slope * d))
        forecast.append({"day": d, "projected_pct": round(projected, 3)})
    trend = "improving" if slope > 0.01 else ("declining" if slope < -0.01 else "stable")
    will_breach = any(f["projected_pct"] < 99.0 for f in forecast)
    return {"forecast": forecast, "trend": trend, "current_pct": history[-1],
            "will_breach": will_breach, "slope": round(slope, 4)}
