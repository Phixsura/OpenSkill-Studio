"""Fleet AI QA — track question answering service."""
from __future__ import annotations
def fleet_ai_qa(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    questions_24h = sum(s.get("questions_24h", 0) for s in services)
    accuracy = round(sum(s.get("accuracy_pct", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "questions_24h": questions_24h,
            "accuracy": accuracy, "reliable": accuracy >= 90}
