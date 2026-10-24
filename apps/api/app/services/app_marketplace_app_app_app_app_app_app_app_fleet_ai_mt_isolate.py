"""Fleet AI Multi-Tenant Isolation — track tenant data and compute isolation."""
from __future__ import annotations
def fleet_ai_mt_isolation(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    tenants = sum(s.get("tenants", 0) for s in systems)
    isolated = sum(s.get("isolated", 0) for s in systems)
    breaches = sum(s.get("breaches", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "tenants": tenants,
            "isolated": isolated, "breaches": breaches, "secure": breaches == 0 and isolated == tenants}
