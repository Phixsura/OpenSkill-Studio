"""Fleet AI Access Governance v7 — track ultimate access management."""
from __future__ import annotations
def fleet_ai_access_governance_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    users = sum(s.get("users", 0) for s in systems)
    roles = sum(s.get("roles", 0) for s in systems)
    reviews_30d = sum(s.get("reviews", 0) for s in systems)
    excessive = sum(s.get("excessive", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "users": users,
            "roles": roles, "reviews": reviews_30d, "excessive": excessive, "clean": excessive == 0}
