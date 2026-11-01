"""Fleet Network ACL v9 — track network access control lists."""
from __future__ import annotations
def fleet_network_acl_v9(acls: list[dict]) -> dict:
    active = [a for a in acls if a.get("active")]
    allow_rules = sum(a.get("allow_rules", 0) for a in acls)
    deny_rules = sum(a.get("deny_rules", 0) for a in acls)
    return {"acls": len(acls), "active": len(active), "allow_rules": allow_rules,
            "deny_rules": deny_rules, "healthy": True}
