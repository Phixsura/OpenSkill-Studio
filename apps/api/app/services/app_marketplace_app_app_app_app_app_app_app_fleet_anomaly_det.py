"""Fleet anomaly detection — statistical anomaly detection."""
from __future__ import annotations
def fleet_anomaly_detect(values: list[float], threshold_sigma: float = 2.0) -> dict:
    if len(values) < 3:
        return {"anomalies": 0, "total": len(values), "mean": 0, "std": 0}
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = variance ** 0.5
    anomalies = [v for v in values if abs(v - mean) > threshold_sigma * std]
    return {"anomalies": len(anomalies), "total": len(values),
            "mean": round(mean, 2), "std": round(std, 2)}
