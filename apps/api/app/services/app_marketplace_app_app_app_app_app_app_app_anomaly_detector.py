"""Anomaly detector — statistical anomaly detection using z-score."""
from __future__ import annotations
import math


def detect_anomalies(values: list[float], *, threshold: float = 2.0,
                      labels: list[str] | None = None) -> dict:
    if len(values) < 3:
        return {"anomalies": [], "count": 0, "error": "Need at least 3 data points"}
    n = len(values)
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance) if variance > 0 else 0.001
    anomalies = []
    for i, v in enumerate(values):
        z = abs(v - mean) / std
        if z >= threshold:
            label = labels[i] if labels and i < len(labels) else f"point_{i}"
            anomalies.append({"index": i, "label": label, "value": v,
                              "z_score": round(z, 2), "direction": "high" if v > mean else "low"})
    return {
        "mean": round(mean, 2), "std": round(std, 2),
        "threshold": threshold, "total_points": n,
        "anomalies": anomalies, "count": len(anomalies),
        "anomaly_rate": round(len(anomalies) / n * 100, 1),
    }
