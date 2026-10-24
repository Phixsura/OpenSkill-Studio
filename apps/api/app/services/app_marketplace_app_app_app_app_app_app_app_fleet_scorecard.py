"""Fleet Scorecard — track platform engineering maturity scorecard."""
from __future__ import annotations
def fleet_scorecard(dimensions: dict) -> dict:
    scores = list(dimensions.values())
    avg = round(sum(scores) / max(len(scores), 1), 1)
    top = max(dimensions, key=lambda k: dimensions[k]) if dimensions else None
    bottom = min(dimensions, key=lambda k: dimensions[k]) if dimensions else None
    grade = "A+" if avg >= 95 else ("A" if avg >= 90 else ("B" if avg >= 80 else ("C" if avg >= 70 else "D")))
    return {"dimensions": len(dimensions), "avg_score": avg, "top": top,
            "bottom": bottom, "grade": grade}
