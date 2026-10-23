"""Usage anomaly detector — detect abnormal usage patterns."""

import math


def detect_anomalies(*, data_points: list[float], sensitivity: float = 2.0) -> dict:
    if len(data_points) < 5:
        return {"error": "Need at least 5 data points"}
    mean = sum(data_points) / len(data_points)
    variance = sum((x - mean) ** 2 for x in data_points) / len(data_points)
    std_dev = math.sqrt(variance) if variance > 0 else 0.01
    anomalies = []
    for i, val in enumerate(data_points):
        z_score = (val - mean) / std_dev
        if abs(z_score) >= sensitivity:
            anomalies.append({
                "index": i,
                "value": val,
                "z_score": round(z_score, 2),
                "type": "spike" if z_score > 0 else "drop",
                "deviation_pct": round(abs(val - mean) / mean * 100, 1) if mean != 0 else 0,
            })
    return {
        "mean": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "anomaly_rate": round(len(anomalies) / len(data_points) * 100, 1),
        "total_points": len(data_points),
    }
