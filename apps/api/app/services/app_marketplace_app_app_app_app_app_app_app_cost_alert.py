"""Cost anomaly alerter — alert on unusual cost spikes."""
from __future__ import annotations
import math


def check_cost_anomaly(daily_costs: list[float], current: float, sigma: float = 2.0) -> dict:
    if len(daily_costs) < 3:
        return {"anomaly": False, "reason": "insufficient_data"}
    mean = sum(daily_costs) / len(daily_costs)
    std = math.sqrt(sum((x - mean) ** 2 for x in daily_costs) / len(daily_costs))
    z = (current - mean) / max(std, 0.01)
    anomaly = abs(z) > sigma
    return {"anomaly": anomaly, "current": current, "mean": round(mean, 2),
            "std": round(std, 2), "z_score": round(z, 2),
            "type": "spike" if z > 0 else "drop" if z < 0 else "normal",
            "alert": anomaly and z > 0}


def cost_alert_summary(alerts: list[dict]) -> dict:
    spikes = sum(1 for a in alerts if a.get("type") == "spike" and a.get("anomaly"))
    return {"total_checked": len(alerts), "anomalies": sum(1 for a in alerts if a.get("anomaly")),
            "spikes": spikes, "any_alert": spikes > 0}
