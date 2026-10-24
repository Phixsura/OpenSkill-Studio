"""Service health trend — track health score changes over time."""
from __future__ import annotations


def calculate_health_trend(scores: list[float], periods: int = 7) -> dict:
    if len(scores) < 2:
        return {"trend": "insufficient", "scores": scores}
    recent = scores[-periods:] if len(scores) >= periods else scores
    avg_recent = round(sum(recent) / len(recent), 1)
    first_half = scores[:len(scores)//2]
    second_half = scores[len(scores)//2:]
    avg_first = round(sum(first_half) / max(len(first_half), 1), 1)
    avg_second = round(sum(second_half) / max(len(second_half), 1), 1)
    delta = round(avg_second - avg_first, 1)
    trend = "improving" if delta > 2 else "declining" if delta < -2 else "stable"
    return {"trend": trend, "current_avg": avg_recent, "delta": delta,
            "latest": scores[-1], "min": min(scores), "max": max(scores),
            "data_points": len(scores)}


def health_forecast(scores: list[float], forecast_periods: int = 3) -> dict:
    if len(scores) < 3:
        return {"forecast": []}
    avg_change = (scores[-1] - scores[0]) / (len(scores) - 1)
    forecast = []
    last = scores[-1]
    for i in range(forecast_periods):
        projected = round(min(100, max(0, last + avg_change * (i + 1))), 1)
        forecast.append({"period": i + 1, "projected": projected})
    return {"forecast": forecast, "avg_change": round(avg_change, 2)}
