"""Platform usage forecaster — predict future usage using linear regression."""
from __future__ import annotations


def forecast_usage(data_points: list[dict], *, months_ahead: int = 6) -> dict:
    if len(data_points) < 2:
        return {"error": "Need at least 2 data points"}
    xs = [i for i in range(len(data_points))]
    ys = [d.get("value", 0) for d in data_points]
    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in zip(xs, ys))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        slope = 0
        intercept = sum_y / n
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
    predictions = []
    for m in range(1, months_ahead + 1):
        x = n + m - 1
        predicted = round(slope * x + intercept, 1)
        predictions.append({"month": m, "predicted": max(0, predicted)})
    trend = "growing" if slope > 0 else "declining" if slope < 0 else "flat"
    growth_rate = round(slope / max(intercept, 1) * 100, 1) if intercept else 0
    return {
        "historical_points": n, "slope": round(slope, 2),
        "intercept": round(intercept, 2), "trend": trend,
        "growth_rate_pct": growth_rate,
        "predictions": predictions,
        "predicted_final": predictions[-1]["predicted"] if predictions else 0,
    }
