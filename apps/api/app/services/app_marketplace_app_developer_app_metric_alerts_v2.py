"""Metric alerts v2 — anomaly detection with dynamic thresholds."""

import math


def compute_dynamic_threshold(*, values: list[float], sensitivity: float = 2.0) -> dict:
    if len(values) < 3:
        return {"mean": 0, "std": 0, "upper": float("inf"), "lower": 0}
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)
    return {"mean": round(mean, 2), "std": round(std, 2),
            "upper": round(mean + sensitivity * std, 2),
            "lower": round(max(0, mean - sensitivity * std), 2)}


def detect_anomaly(*, value: float, threshold: dict) -> dict:
    is_anomaly = value > threshold["upper"] or value < threshold["lower"]
    direction = "above" if value > threshold["upper"] else "below" if value < threshold["lower"] else "normal"
    deviation = round(abs(value - threshold["mean"]) / max(threshold["std"], 0.01), 1)
    return {"is_anomaly": is_anomaly, "direction": direction, "value": value,
            "deviation_sigma": deviation, "severity": "critical" if deviation > 3 else "warning" if deviation > 2 else "info"}


def build_alert_history(*, alerts: list[dict], limit: int = 50) -> dict:
    sorted_alerts = sorted(alerts, key=lambda a: a.get("timestamp", ""), reverse=True)[:limit]
    anomalies = sum(1 for a in alerts if a.get("is_anomaly"))
    return {"alerts": sorted_alerts, "total": len(alerts), "anomaly_count": anomalies,
            "anomaly_rate": round(anomalies / max(len(alerts), 1) * 100, 1)}
