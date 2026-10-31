"""Endpoint traffic forecast — forecast per-endpoint traffic growth."""
from __future__ import annotations


def forecast_endpoint_traffic(endpoint: str, daily_rps: list[float], days_ahead: int = 7) -> dict:
    if len(daily_rps) < 3:
        return {"endpoint": endpoint, "forecast": [], "trend": "insufficient_data"}
    avg = sum(daily_rps) / len(daily_rps)
    recent = sum(daily_rps[-3:]) / 3
    growth = (recent - avg) / max(avg, 0.01)
    forecast = []
    current = daily_rps[-1]
    for d in range(1, days_ahead + 1):
        current *= (1 + growth / 7)
        forecast.append({"day": d, "projected_rps": round(current, 1)})
    trend = "growing" if growth > 0.05 else ("declining" if growth < -0.05 else "stable")
    return {"endpoint": endpoint, "forecast": forecast, "trend": trend,
            "current_rps": daily_rps[-1], "growth_rate": round(growth * 100, 1)}
