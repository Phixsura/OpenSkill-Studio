"""Fleet AI Ethics v8 — track ultimate responsible AI practices."""
from __future__ import annotations
def fleet_ai_ethics_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    assessments = sum(s.get("assessments", 0) for s in systems)
    principles = sum(s.get("principles", 0) for s in systems)
    score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "assessments": assessments,
            "principles": principles, "score": score, "ethical": score > 95}
