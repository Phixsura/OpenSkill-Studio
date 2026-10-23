"""Cost anomaly detector — detect unusual spending patterns."""
from __future__ import annotations
import math


def detect_anomalies(daily_costs: list[float], threshold_sigma: float = 2.0) -> dict:
    if len(daily_costs) < 3:
        return {"anomalies": [], "mean": 0, "std": 0, "checked": len(daily_costs)}
    mean = sum(daily_costs) / len(daily_costs)
    variance = sum((x - mean) ** 2 for x in daily_costs) / len(daily_costs)
    std = math.sqrt(variance)
    anomalies = []
    for i, cost in enumerate(daily_costs):
        z_score = (cost - mean) / max(std, 0.01)
        if abs(z_score) > threshold_sigma:
            anomalies.append({"day": i, "cost": cost, "z_score": round(z_score, 2),
                               "direction": "spike" if z_score > 0 else "drop"})
    return {"anomalies": anomalies, "anomaly_count": len(anomalies),
            "mean": round(mean, 2), "std": round(std, 2),
            "checked": len(daily_costs), "has_anomaly": len(anomalies) > 0}


def estimate_savings(anomalies: list[dict], mean: float) -> dict:
    total_excess = sum(max(0, a["cost"] - mean) for a in anomalies if a["direction"] == "spike")
    return {"potential_savings": round(total_excess, 2),
            "spike_count": sum(1 for a in anomalies if a["direction"] == "spike"),
            "display": f"${total_excess:,.2f}"}
