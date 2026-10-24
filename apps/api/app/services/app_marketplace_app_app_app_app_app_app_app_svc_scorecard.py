"""Service scorecard — grade services across multiple dimensions."""
from __future__ import annotations

DIMENSIONS = ["reliability", "performance", "security", "observability", "documentation"]


def score_service(service: str, scores: dict[str, int]) -> dict:
    results = []
    total = 0
    for dim in DIMENSIONS:
        s = min(scores.get(dim, 0), 100)
        total += s
        results.append({"dimension": dim, "score": s,
                         "grade": "A" if s >= 90 else "B" if s >= 75 else "C" if s >= 60 else "D"})
    avg = round(total / len(DIMENSIONS))
    overall = "A" if avg >= 90 else "B" if avg >= 75 else "C" if avg >= 60 else "D"
    return {"service": service, "dimensions": results, "avg_score": avg,
            "overall_grade": overall}
