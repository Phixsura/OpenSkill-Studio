"""Error rate anomaly detector — detect unusual error rate spikes."""
from __future__ import annotations
import math


def detect_error_anomaly(error_rates: list[float], sensitivity: float = 2.0) -> dict:
    if len(error_rates) < 5:
        return {"anomaly": False, "reason": "insufficient_data"}
    mean = sum(error_rates) / len(error_rates)
    std = math.sqrt(sum((x - mean) ** 2 for x in error_rates) / len(error_rates))
    latest = error_rates[-1]
    z_score = (latest - mean) / max(std, 0.001)
    anomaly = z_score > sensitivity
    return {"anomaly": anomaly, "latest": latest, "mean": round(mean, 3),
            "std": round(std, 3), "z_score": round(z_score, 2),
            "threshold": sensitivity}


def error_rate_trend(rates: list[float]) -> dict:
    if len(rates) < 2:
        return {"trend": "stable"}
    recent = sum(rates[-3:]) / min(3, len(rates))
    older = sum(rates[:3]) / min(3, len(rates))
    if recent > older * 1.5:
        return {"trend": "worsening", "recent_avg": round(recent, 3), "older_avg": round(older, 3)}
    elif recent < older * 0.5:
        return {"trend": "improving", "recent_avg": round(recent, 3), "older_avg": round(older, 3)}
    return {"trend": "stable", "recent_avg": round(recent, 3), "older_avg": round(older, 3)}
