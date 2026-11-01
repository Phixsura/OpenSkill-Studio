"""Fleet AI Access Control — track AI-powered authorization and RBAC."""
from __future__ import annotations
def fleet_ai_access_control(controllers: list[dict]) -> dict:
    active = [c for c in controllers if c.get("active", True)]
    policies = sum(c.get("policies", 0) for c in controllers)
    evaluations_24h = sum(c.get("evaluations_24h", 0) for c in controllers)
    denied_24h = sum(c.get("denied_24h", 0) for c in controllers)
    return {"controllers": len(controllers), "active": len(active), "policies": policies,
            "evaluations_24h": evaluations_24h, "denied_24h": denied_24h, "enforcing": len(active) == len(controllers)}
