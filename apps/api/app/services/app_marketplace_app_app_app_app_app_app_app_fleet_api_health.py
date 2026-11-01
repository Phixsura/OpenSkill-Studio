"""Fleet API health score — composite API quality metric."""
from __future__ import annotations
def fleet_api_health_score(metrics: dict) -> dict:
    avail = metrics.get("availability_pct", 99.9)
    latency_ok = 100 - min(metrics.get("p99_ms", 0) / 10, 100)
    error_ok = 100 - min(metrics.get("error_rate_pct", 0) * 10, 100)
    score = round((avail + latency_ok + error_ok) / 3, 1)
    return {"score": score, "availability": avail,
            "grade": "A" if score >= 90 else ("B" if score >= 75 else "C")}
