"""Fleet AI Question Answerer — track extractive and generative QA."""
from __future__ import annotations
def fleet_ai_qa(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    questions_24h = sum(s.get("questions_24h", 0) for s in systems)
    accuracy = round(sum(s.get("accuracy", 0) for s in systems) / max(len(systems), 1), 1)
    sources_used = sum(s.get("sources", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "questions_24h": questions_24h,
            "accuracy": accuracy, "sources": sources_used, "knowledgeable": accuracy > 85}
