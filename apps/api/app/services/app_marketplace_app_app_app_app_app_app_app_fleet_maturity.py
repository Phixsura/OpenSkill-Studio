"""Fleet maturity score — platform engineering maturity assessment."""
from __future__ import annotations
def fleet_maturity_score(dimensions: dict) -> dict:
    scores = [dimensions.get(d, 0) for d in ["observability", "reliability", "security", "automation", "governance"]]
    avg = round(sum(scores) / max(len(scores), 1), 1)
    level = "Expert" if avg >= 90 else ("Advanced" if avg >= 70 else ("Intermediate" if avg >= 50 else "Beginner"))
    return {"score": avg, "level": level, "dimensions": dimensions}
