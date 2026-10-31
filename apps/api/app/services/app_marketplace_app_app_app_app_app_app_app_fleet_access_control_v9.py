"""Fleet Access Control v9 — track RBAC policy enforcement."""
from __future__ import annotations
def fleet_access_control_v9(policies: list[dict]) -> dict:
    active = [p for p in policies if p.get("active", True)]
    denials = sum(p.get("denials", 0) for p in policies)
    roles = len({p.get("role") for p in policies if p.get("role")})
    return {"policies": len(policies), "active": len(active), "denials": denials,
            "unique_roles": roles, "healthy": True}
