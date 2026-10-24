"""Fleet AI Anomaly — track ML-powered anomaly detection."""
from __future__ import annotations
def fleet_ai_anomaly(detectors: list[dict]) -> dict:
    active = [d for d in detectors if d.get("active", True)]
    anomalies_24h = sum(d.get("anomalies_24h", 0) for d in detectors)
    data_points = sum(d.get("data_points_24h", 0) for d in detectors)
    return {"detectors": len(detectors), "active": len(active), "anomalies_24h": anomalies_24h,
            "data_points_24h": data_points, "all_active": len(active) == len(detectors)}
