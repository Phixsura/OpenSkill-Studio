"""Service dependency health score — composite score from all dependency health."""
from __future__ import annotations


def calculate_dep_health(dependencies: list[dict]) -> dict:
    if not dependencies:
        return {"score": 100, "status": "healthy", "deps": 0}
    scores = []
    for dep in dependencies:
        latency_score = max(0, 100 - dep.get("latency_ms", 0) / 10)
        error_score = max(0, 100 - dep.get("error_rate_pct", 0) * 20)
        avail_score = dep.get("availability_pct", 100)
        dep_score = round((latency_score * 0.3 + error_score * 0.4 + avail_score * 0.3), 1)
        scores.append({"name": dep["name"], "score": dep_score,
                        "latency_ms": dep.get("latency_ms", 0),
                        "error_rate": dep.get("error_rate_pct", 0)})
    overall = round(sum(s["score"] for s in scores) / len(scores), 1)
    status = "healthy" if overall >= 90 else ("degraded" if overall >= 70 else "critical")
    weakest = min(scores, key=lambda s: s["score"])
    return {"score": overall, "status": status, "deps": len(scores),
            "details": sorted(scores, key=lambda s: s["score"]),
            "weakest": weakest["name"]}
