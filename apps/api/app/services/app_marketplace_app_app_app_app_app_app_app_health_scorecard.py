"""Platform health scorecard — aggregate health across all dimensions."""
from __future__ import annotations

def compute_scorecard(dimensions: dict[str, float]) -> dict:
    scores = {k: min(100, max(0, v)) for k, v in dimensions.items()}
    overall = round(sum(scores.values()) / max(len(scores), 1), 1)
    grade = "A" if overall >= 90 else ("B" if overall >= 75 else ("C" if overall >= 60 else "F"))
    worst = min(scores.items(), key=lambda x: x[1]) if scores else ("none", 0)
    return {"overall": overall, "grade": grade, "dimensions": scores,
            "weakest": worst[0], "weakest_score": worst[1]}
