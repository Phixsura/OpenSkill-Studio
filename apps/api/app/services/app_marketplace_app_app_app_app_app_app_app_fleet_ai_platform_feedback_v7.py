"""Fleet AI Feedback v7 — track AI platform user feedback loop."""
from __future__ import annotations
def fleet_ai_feedback_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    feedback_24h = sum(s.get("feedback", 0) for s in systems)
    positive = sum(s.get("positive", 0) for s in systems)
    actioned = sum(s.get("actioned", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "feedback": feedback_24h,
            "positive": positive, "actioned": actioned, "responsive": actioned > 0}
