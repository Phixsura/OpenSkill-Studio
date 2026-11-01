"""Anomaly detection scorer — score data points for anomalies."""
from __future__ import annotations
import math


def z_score_detect(values: list[float], threshold: float = 3.0) -> dict:
    n = len(values)
    if n < 3:
        return {"anomalies": [], "mean": 0, "std": 0}
    mean = sum(values) / n
    std = math.sqrt(sum((x - mean) ** 2 for x in values) / n)
    anomalies = []
    for i, v in enumerate(values):
        z = abs(v - mean) / max(std, 0.001)
        if z > threshold:
            anomalies.append({"index": i, "value": v, "z_score": round(z, 2)})
    return {"anomalies": anomalies, "mean": round(mean, 2),
            "std": round(std, 2), "total": n, "threshold": threshold}


def iqr_detect(values: list[float], k: float = 1.5) -> dict:
    s = sorted(values)
    n = len(s)
    q1 = s[n // 4]
    q3 = s[3 * n // 4]
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    outliers = [{"value": v, "index": values.index(v)}
                for v in values if v < lower or v > upper]
    return {"outliers": outliers, "q1": q1, "q3": q3, "iqr": iqr,
            "lower": round(lower, 2), "upper": round(upper, 2)}
