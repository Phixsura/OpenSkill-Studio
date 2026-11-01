"""Fleet health score — composite health score for the entire fleet."""
from __future__ import annotations
def fleet_health_score(services: list[dict]) -> dict:
    scores = [s.get("health_score", 0) for s in services]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    grade = "A" if avg >= 90 else ("B" if avg >= 75 else ("C" if avg >= 60 else "F"))
    return {"score": avg, "grade": grade, "services": len(services)}
