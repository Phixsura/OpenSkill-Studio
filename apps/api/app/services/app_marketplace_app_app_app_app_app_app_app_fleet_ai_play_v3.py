"""Fleet AI Playground v3 — track collaborative AI experimentation."""
from __future__ import annotations
def fleet_ai_playground_v3(playgrounds: list[dict]) -> dict:
    active = [p for p in playgrounds if p.get("active", True)]
    sessions_24h = sum(p.get("sessions_24h", 0) for p in playgrounds)
    collaborators = sum(p.get("collaborators", 0) for p in playgrounds)
    shared_notebooks = sum(p.get("notebooks", 0) for p in playgrounds)
    return {"playgrounds": len(playgrounds), "active": len(active), "sessions_24h": sessions_24h,
            "collaborators": collaborators, "notebooks": shared_notebooks, "collaborative": collaborators > 10}
