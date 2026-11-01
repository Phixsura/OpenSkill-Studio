"""Fleet AI Community v7 — track AI platform developer community."""
from __future__ import annotations
def fleet_ai_community_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    members = sum(s.get("members", 0) for s in systems)
    contributors = sum(s.get("contributors", 0) for s in systems)
    discussions = sum(s.get("discussions_30d", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "members": members,
            "contributors": contributors, "discussions": discussions, "vibrant": members > 10000}
