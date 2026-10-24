"""Platform health score — composite health score from multiple signals."""
from __future__ import annotations


def calculate_health_score(signals: dict) -> dict:
    weights = {"uptime": 30, "error_rate": 25, "latency": 20, "saturation": 15, "freshness": 10}
    scores = {}
    uptime = signals.get("uptime_pct", 100)
    scores["uptime"] = min(100, uptime / 99.9 * 100)
    err = signals.get("error_rate_pct", 0)
    scores["error_rate"] = max(0, 100 - err * 20)
    lat = signals.get("p99_ms", 0)
    scores["latency"] = max(0, 100 - lat / 10)
    sat = signals.get("cpu_pct", 0)
    scores["saturation"] = max(0, 100 - sat)
    fresh = signals.get("data_age_minutes", 0)
    scores["freshness"] = max(0, 100 - fresh)
    total = sum(scores[k] * weights[k] / 100 for k in weights)
    grade = "A" if total >= 90 else ("B" if total >= 75 else ("C" if total >= 60 else ("D" if total >= 40 else "F")))
    return {"score": round(total, 1), "grade": grade, "breakdown": {k: round(v, 1) for k, v in scores.items()}}
