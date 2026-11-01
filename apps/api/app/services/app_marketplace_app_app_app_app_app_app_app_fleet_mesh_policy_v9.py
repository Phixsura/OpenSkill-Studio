"""Fleet Mesh Policy v9 — track service mesh authorization policies."""
from __future__ import annotations
def fleet_mesh_policy_v9(policies: list[dict]) -> dict:
    enforced = [p for p in policies if p.get("enforced")]
    allow = [p for p in policies if p.get("action") == "allow"]
    deny = [p for p in policies if p.get("action") == "deny"]
    return {"total": len(policies), "enforced": len(enforced), "allow": len(allow),
            "deny": len(deny), "healthy": len(enforced) == len(policies)}
