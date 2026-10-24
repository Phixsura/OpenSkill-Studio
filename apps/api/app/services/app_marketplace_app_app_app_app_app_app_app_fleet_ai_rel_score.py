"""Fleet AI Reliability Score — track composite platform reliability metric."""
from __future__ import annotations
def fleet_ai_reliability_score(scorers: list[dict]) -> dict:
    active = [s for s in scorers if s.get("active", True)]
    overall = round(sum(s.get("score", 0) for s in scorers) / max(len(scorers), 1), 1)
    availability = round(sum(s.get("availability", 0) for s in scorers) / max(len(scorers), 1), 3)
    durability = round(sum(s.get("durability", 0) for s in scorers) / max(len(scorers), 1), 3)
    return {"scorers": len(scorers), "active": len(active), "score": overall,
            "availability": availability, "durability": durability, "excellent": overall > 95}
