"""Multi-region failover — manage regional failover and routing."""
from __future__ import annotations


def create_region_config(regions: list[dict]) -> dict:
    primary = [r for r in regions if r.get("role") == "primary"]
    standby = [r for r in regions if r.get("role") == "standby"]
    return {"regions": regions, "primary": primary[0]["name"] if primary else None,
            "standby_count": len(standby), "total_regions": len(regions)}


def check_failover_needed(regions: list[dict]) -> dict:
    primary = next((r for r in regions if r.get("role") == "primary"), None)
    if not primary:
        return {"failover_needed": True, "reason": "no_primary"}
    if not primary.get("healthy", True):
        candidates = [r for r in regions if r.get("role") == "standby" and r.get("healthy")]
        return {"failover_needed": True, "reason": "primary_unhealthy",
                "primary": primary["name"],
                "candidate": candidates[0]["name"] if candidates else None}
    return {"failover_needed": False, "primary": primary["name"]}


def execute_failover(regions: list[dict], new_primary: str) -> dict:
    changes = []
    for r in regions:
        if r["name"] == new_primary:
            old_role = r["role"]
            r["role"] = "primary"
            changes.append({"region": r["name"], "from": old_role, "to": "primary"})
        elif r.get("role") == "primary":
            r["role"] = "standby"
            changes.append({"region": r["name"], "from": "primary", "to": "standby"})
    return {"executed": True, "new_primary": new_primary, "changes": changes}
