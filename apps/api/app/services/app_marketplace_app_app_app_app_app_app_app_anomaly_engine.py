"""Anomaly detection engine — detect anomalies across platform metrics."""
from __future__ import annotations
import math


def detect_anomalies(metrics: dict[str, list[float]], sigma: float = 2.0) -> dict:
    results = []
    for name, values in metrics.items():
        if len(values) < 3:
            continue
        mean = sum(values) / len(values)
        std = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        latest = values[-1]
        z = (latest - mean) / max(std, 0.01)
        is_anomaly = abs(z) > sigma
        if is_anomaly:
            results.append({"metric": name, "latest": latest, "mean": round(mean, 2),
                             "std": round(std, 2), "z_score": round(z, 2),
                             "type": "high" if z > 0 else "low"})
    return {"anomalies": results, "count": len(results),
            "metrics_checked": len(metrics), "has_anomaly": len(results) > 0}
