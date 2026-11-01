"""Fleet AI Ethics v7 — track responsible AI and ethical AI practices."""
from __future__ import annotations
def fleet_ai_ethics_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    assessments = sum(s.get("assessments", 0) for s in systems)
    principles = sum(s.get("principles", 0) for s in systems)
    score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "assessments": assessments,
            "principles": principles, "score": score, "ethical": score > 90}
