"""Health trend predictor — predict future health based on historical data."""
from __future__ import annotations


def predict_health(snapshots: list[float], forecast_periods: int = 7) -> dict:
    if len(snapshots) < 3:
        return {"forecast": [], "trend": "insufficient_data"}
    n = len(snapshots)
    avg = sum(snapshots) / n
    recent = sum(snapshots[-3:]) / 3
    older = sum(snapshots[:3]) / 3
    slope = (recent - older) / max(n, 1)
    forecast = []
    current = snapshots[-1]
    for i in range(1, forecast_periods + 1):
        projected = max(0, min(100, current + slope * i))
        forecast.append({"period": i, "projected": round(projected, 2)})
    trend = "improving" if slope > 0.1 else ("declining" if slope < -0.1 else "stable")
    will_breach = any(f["projected"] < 99.0 for f in forecast)
    return {"forecast": forecast, "trend": trend, "current": snapshots[-1],
            "slope": round(slope, 3), "will_breach_sla": will_breach}
