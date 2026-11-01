"""Service reliability score — composite reliability from multiple dimensions."""
from __future__ import annotations


def calculate_reliability(metrics: dict) -> dict:
    uptime = min(100, metrics.get("uptime_pct", 100))
    error = max(0, 100 - metrics.get("error_rate_pct", 0) * 10)
    latency = max(0, 100 - metrics.get("p99_ms", 0) / 20)
    recovery = max(0, 100 - metrics.get("mttr_minutes", 0))
    incidents = max(0, 100 - metrics.get("incidents_30d", 0) * 10)
    weights = {"uptime": 0.3, "error_rate": 0.25, "latency": 0.2, "recovery": 0.15, "incidents": 0.1}
    score = round(uptime * weights["uptime"] + error * weights["error_rate"] +
                  latency * weights["latency"] + recovery * weights["recovery"] +
                  incidents * weights["incidents"], 1)
    grade = "A" if score >= 90 else ("B" if score >= 75 else ("C" if score >= 60 else "F"))
    return {"score": score, "grade": grade,
            "breakdown": {"uptime": round(uptime, 1), "error_rate": round(error, 1),
                          "latency": round(latency, 1), "recovery": round(recovery, 1),
                          "incidents": round(incidents, 1)},
            "service": metrics.get("service", "")}
