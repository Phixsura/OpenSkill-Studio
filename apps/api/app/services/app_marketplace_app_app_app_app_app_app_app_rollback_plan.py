"""Deployment rollback planner — plan and execute rollbacks safely."""
from __future__ import annotations


def plan_rollback(current: dict, previous: dict, changes: list[dict]) -> dict:
    db_migrations = [c for c in changes if c.get("type") == "migration"]
    has_irreversible = any(c.get("irreversible") for c in db_migrations)
    steps = []
    if not has_irreversible and db_migrations:
        steps.append({"action": "rollback_migrations", "count": len(db_migrations)})
    steps.append({"action": "deploy_previous", "version": previous["version"],
                  "image": previous.get("image", "")})
    steps.append({"action": "verify_health", "timeout_seconds": 60})
    steps.append({"action": "update_routing", "target": previous["version"]})
    risk = "high" if has_irreversible else ("medium" if db_migrations else "low")
    return {"current_version": current["version"],
            "target_version": previous["version"],
            "steps": steps, "risk": risk,
            "has_irreversible_migrations": has_irreversible,
            "estimated_minutes": len(steps) * 2}


def compare_versions(v1: str, v2: str) -> dict:
    p1 = [int(x) for x in v1.split(".")]
    p2 = [int(x) for x in v2.split(".")]
    if p1 > p2:
        direction = "downgrade"
    elif p1 < p2:
        direction = "upgrade"
    else:
        direction = "same"
    return {"from": v1, "to": v2, "direction": direction}
