"""Fleet AI Anomaly Detection — track ML-based anomaly detection systems."""
from __future__ import annotations
def fleet_ai_anomaly(detectors: list[dict]) -> dict:
    active = [d for d in detectors if d.get("active", True)]
    metrics_monitored = sum(d.get("metrics", 0) for d in detectors)
    anomalies_24h = sum(d.get("anomalies_24h", 0) for d in detectors)
    false_positive_rate = round(sum(d.get("fp_rate", 0) for d in detectors) / max(len(detectors), 1), 2)
    return {"detectors": len(detectors), "active": len(active), "metrics": metrics_monitored,
            "anomalies_24h": anomalies_24h, "fp_rate": false_positive_rate, "precise": false_positive_rate < 5}
