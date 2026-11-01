"""Service operational score — unified operational excellence score."""
from __future__ import annotations


def calculate_ops_score(metrics: dict) -> dict:
    categories = {
        "reliability": min(100, metrics.get("uptime_pct", 100)),
        "performance": max(0, 100 - metrics.get("p99_ms", 0) / 10),
        "observability": metrics.get("observability_pct", 0),
        "documentation": metrics.get("doc_coverage_pct", 0),
        "automation": metrics.get("automation_pct", 0),
        "security": metrics.get("security_score", 0),
    }
    weights = {"reliability": 25, "performance": 20, "observability": 15,
               "documentation": 10, "automation": 15, "security": 15}
    score = sum(categories[k] * weights[k] / 100 for k in categories)
    score = round(score, 1)
    grade = "A" if score >= 90 else ("B" if score >= 75 else ("C" if score >= 60 else "F"))
    return {"score": score, "grade": grade, "categories": {k: round(v, 1) for k, v in categories.items()}}
