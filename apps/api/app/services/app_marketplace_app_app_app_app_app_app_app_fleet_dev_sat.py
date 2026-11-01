"""Fleet developer satisfaction — track developer happiness metrics."""
from __future__ import annotations
def fleet_dev_satisfaction(surveys: list[dict]) -> dict:
    scores = [s.get("satisfaction", 0) for s in surveys]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    happy = [s for s in scores if s >= 4]
    return {"responses": len(surveys), "avg_score": avg,
            "happy_pct": round(len(happy) / max(len(surveys), 1) * 100, 1),
            "good": avg >= 4}
