"""Fleet AI Engagement v7 — track user engagement and stickiness."""
from __future__ import annotations
def fleet_ai_engagement_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    dau_mau = round(sum(t.get("dau_mau", 0) for t in trackers) / max(len(trackers), 1), 1)
    sessions_per_user = round(sum(t.get("sessions", 0) for t in trackers) / max(len(trackers), 1), 1)
    time_per_session = round(sum(t.get("time_min", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "dau_mau": dau_mau,
            "sessions": sessions_per_user, "time_min": time_per_session, "engaged": dau_mau > 30}
