"""Fleet platform summary — executive dashboard of fleet health."""
from __future__ import annotations
def fleet_platform_summary(metrics: dict) -> dict:
    score = 100
    if metrics.get("incidents_open", 0) > 0: score -= 20
    if metrics.get("slo_violations", 0) > 0: score -= 15
    if metrics.get("security_issues", 0) > 0: score -= 25
    grade = "A" if score >= 90 else ("B" if score >= 75 else ("C" if score >= 60 else "F"))
    return {"score": max(score, 0), "grade": grade, "metrics": metrics}
