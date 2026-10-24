"""Fleet Traffic Policy v9 — track traffic management policies."""
from __future__ import annotations
def fleet_traffic_policy_v9(policies: list[dict]) -> dict:
    active = [p for p in policies if p.get("active")]
    weighted = [p for p in policies if p.get("type") == "weighted"]
    header_based = [p for p in policies if p.get("type") == "header"]
    return {"policies": len(policies), "active": len(active), "weighted": len(weighted),
            "header_based": len(header_based), "healthy": len(active) == len(policies)}
