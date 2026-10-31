"""Fleet IP Allowlist v9 — track IP-based access control rules."""
from __future__ import annotations
def fleet_ip_allowlist_v9(rules: list[dict]) -> dict:
    active = [r for r in rules if r.get("active", True)]
    blocked = sum(r.get("blocked_today", 0) for r in rules)
    cidrs = len({r.get("cidr") for r in rules if r.get("cidr")})
    return {"rules": len(rules), "active": len(active), "blocked_today": blocked,
            "unique_cidrs": cidrs, "healthy": True}
