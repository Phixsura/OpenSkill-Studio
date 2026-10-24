"""API usage forecaster — forecast API usage trends."""
from __future__ import annotations


def forecast_usage(daily_usage: list[float], forecast_days: int = 30) -> dict:
    if len(daily_usage) < 3:
        return {"forecast": [], "trend": "insufficient_data"}
    avg = sum(daily_usage) / len(daily_usage)
    recent = sum(daily_usage[-7:]) / min(7, len(daily_usage))
    growth_rate = (recent - avg) / max(avg, 0.01)
    forecast = []
    current = daily_usage[-1]
    for d in range(1, forecast_days + 1):
        current *= (1 + growth_rate / 30)
        forecast.append({"day": d, "projected": round(current)})
    trend = "growing" if growth_rate > 0.01 else ("declining" if growth_rate < -0.01 else "stable")
    return {"forecast": forecast, "trend": trend, "current_daily": round(daily_usage[-1]),
            "projected_30d": round(forecast[-1]["projected"]) if forecast else 0,
            "growth_rate_pct": round(growth_rate * 100, 2)}
