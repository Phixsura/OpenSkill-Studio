"""Fleet API Access Policy v9 — track fine-grained API access control."""
from __future__ import annotations
def fleet_api_access_policy_v9(policies: list[dict]) -> dict:
    enforced = [p for p in policies if p.get("enforced")]
    ip_restricted = [p for p in policies if p.get("ip_restricted")]
    scope_limited = [p for p in policies if p.get("scope_limited")]
    return {"policies": len(policies), "enforced": len(enforced), "ip_restricted": len(ip_restricted),
            "scope_limited": len(scope_limited), "healthy": len(enforced) == len(policies)}
