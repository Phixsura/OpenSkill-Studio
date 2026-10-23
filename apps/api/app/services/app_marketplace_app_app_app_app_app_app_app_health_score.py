"""Health score calculator — composite health scoring for apps."""
from __future__ import annotations


def calculate_health_score(metrics: dict) -> dict:
    weights = {"uptime": 0.30, "error_rate": 0.25, "latency": 0.20,
               "throughput": 0.15, "saturation": 0.10}
    scores = {}
    for metric, weight in weights.items():
        raw = metrics.get(metric, 100)
        scores[metric] = {"raw": raw, "weight": weight, "weighted": round(raw * weight, 2)}
    total = round(sum(s["weighted"] for s in scores.values()), 1)
    grade = "A" if total >= 90 else "B" if total >= 80 else "C" if total >= 70 else "D" if total >= 60 else "F"
    return {"score": total, "grade": grade, "breakdown": scores,
            "status": "healthy" if total >= 80 else "degraded" if total >= 60 else "critical"}


def compare_scores(current: dict, previous: dict) -> dict:
    delta = round(current["score"] - previous["score"], 1)
    return {"current": current["score"], "previous": previous["score"],
            "delta": delta, "improved": delta > 0,
            "grade_change": f"{previous['grade']} → {current['grade']}" if current["grade"] != previous["grade"] else "unchanged"}
