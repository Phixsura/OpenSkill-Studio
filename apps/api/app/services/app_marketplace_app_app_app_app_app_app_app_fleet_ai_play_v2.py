"""Fleet AI Playground v2 — track next-gen interactive AI experimentation."""
from __future__ import annotations
def fleet_ai_playground_v2(playgrounds: list[dict]) -> dict:
    active = [p for p in playgrounds if p.get("active", True)]
    sessions_24h = sum(p.get("sessions_24h", 0) for p in playgrounds)
    shared_sessions = sum(p.get("shared", 0) for p in playgrounds)
    avg_satisfaction = round(sum(p.get("satisfaction", 0) for p in playgrounds) / max(len(playgrounds), 1), 1)
    return {"playgrounds": len(playgrounds), "active": len(active), "sessions_24h": sessions_24h,
            "shared": shared_sessions, "satisfaction": avg_satisfaction, "loved": avg_satisfaction > 4}
