"""Cost anomaly detector — detect unusual spending patterns."""
from __future__ import annotations
import math


def detect_anomalies(daily_costs: list[float], threshold_std: float = 2.0) -> dict:
    if len(daily_costs) < 3:
        return {"anomalies": [], "mean": 0, "std": 0, "status": "insufficient_data"}
    mean = sum(daily_costs) / len(daily_costs)
    variance = sum((x - mean) ** 2 for x in daily_costs) / len(daily_costs)
    std = math.sqrt(variance)
    upper = mean + threshold_std * std
    anomalies = []
    for i, cost in enumerate(daily_costs):
        if cost > upper:
            anomalies.append({"day": i, "cost": round(cost, 2),
                              "deviation": round((cost - mean) / max(std, 0.01), 2),
                              "threshold": round(upper, 2)})
    return {"anomalies": anomalies, "mean": round(mean, 2), "std": round(std, 2),
            "upper_bound": round(upper, 2), "total_days": len(daily_costs),
            "status": "alert" if anomalies else "normal"}


def forecast_monthly(daily_avg: float, days_remaining: int, spent_so_far: float) -> dict:
    projected = spent_so_far + daily_avg * days_remaining
    return {"daily_avg": round(daily_avg, 2), "days_remaining": days_remaining,
            "spent_so_far": round(spent_so_far, 2),
            "projected_total": round(projected, 2)}
