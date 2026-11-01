"""Fleet AI Platform Maturity v7 — track ultimate platform maturity level."""
from __future__ import annotations
def fleet_ai_platform_maturity_v7(assessors: list[dict]) -> dict:
    active = [a for a in assessors if a.get("active", True)]
    level = max((a.get("level", 0) for a in assessors), default=0)
    dimensions = sum(a.get("dimensions", 0) for a in assessors)
    score = round(sum(a.get("score", 0) for a in assessors) / max(len(assessors), 1), 1)
    return {"assessors": len(assessors), "active": len(active), "level": level,
            "dimensions": dimensions, "score": score, "world_class": level == 5 and score > 95}
