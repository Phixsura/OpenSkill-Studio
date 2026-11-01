"""Fleet Boundary — track identity-based access management."""
from __future__ import annotations
def fleet_boundary_status(targets: list[dict]) -> dict:
    active_sessions = sum(t.get("active_sessions", 0) for t in targets)
    authorized = [t for t in targets if t.get("authorized", True)]
    return {"targets": len(targets), "active_sessions": active_sessions,
            "authorized": len(authorized), "all_authorized": len(authorized) == len(targets)}
