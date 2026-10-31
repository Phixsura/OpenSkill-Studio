"""Log anomaly detector — detect unusual patterns in logs."""
from __future__ import annotations
import math


def detect_log_anomalies(log_counts: list[int], sigma_threshold: float = 2.0) -> dict:
    if len(log_counts) < 3:
        return {"anomalies": [], "checked": len(log_counts)}
    mean = sum(log_counts) / len(log_counts)
    variance = sum((x - mean) ** 2 for x in log_counts) / len(log_counts)
    std = math.sqrt(variance) if variance > 0 else 0
    anomalies = []
    for i, count in enumerate(log_counts):
        if std > 0:
            z = (count - mean) / std
            if abs(z) > sigma_threshold:
                anomalies.append({"index": i, "count": count, "z_score": round(z, 2),
                                   "type": "spike" if z > 0 else "drop"})
    return {"anomalies": anomalies, "anomaly_count": len(anomalies),
            "mean": round(mean, 1), "std": round(std, 1),
            "checked": len(log_counts), "has_anomaly": len(anomalies) > 0}
