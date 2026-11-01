"""Fleet AI RBAC v5 — track role-based access control at platform scale."""
from __future__ import annotations
def fleet_ai_rbac_v5(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    roles = sum(e.get("roles", 0) for e in engines)
    permissions = sum(e.get("permissions", 0) for e in engines)
    evaluations_24h = sum(e.get("evals", 0) for e in engines)
    return {"engines": len(engines), "active": len(active), "roles": roles,
            "permissions": permissions, "evals": evaluations_24h, "enforcing": permissions > 0}
