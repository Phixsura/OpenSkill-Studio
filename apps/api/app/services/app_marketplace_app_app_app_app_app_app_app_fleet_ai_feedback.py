"""Fleet AI Feedback Loop — track user feedback collection and model improvement."""
from __future__ import annotations
def fleet_ai_feedback_loop(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    feedback_24h = sum(s.get("feedback_24h", 0) for s in systems)
    thumbs_up = sum(s.get("thumbs_up", 0) for s in systems)
    thumbs_down = sum(s.get("thumbs_down", 0) for s in systems)
    satisfaction = round(thumbs_up / max(thumbs_up + thumbs_down, 1) * 100, 1)
    return {"systems": len(systems), "active": len(active), "feedback_24h": feedback_24h,
            "thumbs_up": thumbs_up, "thumbs_down": thumbs_down, "satisfaction": satisfaction, "positive": satisfaction > 80}
