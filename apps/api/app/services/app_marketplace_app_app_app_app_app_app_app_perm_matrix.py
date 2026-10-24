"""Permission matrix — granular app permission management."""
from __future__ import annotations

RESOURCES = ["users", "projects", "billing", "settings", "analytics", "webhooks"]
ACTIONS = ["read", "write", "delete", "admin"]


def build_permission_matrix(grants: dict[str, list[str]] | None = None) -> dict:
    matrix = []
    granted_count = 0
    for res in RESOURCES:
        res_grants = (grants or {}).get(res, [])
        row = {"resource": res, "actions": {}}
        for act in ACTIONS:
            allowed = act in res_grants
            row["actions"][act] = allowed
            if allowed:
                granted_count += 1
        matrix.append(row)
    total = len(RESOURCES) * len(ACTIONS)
    return {"matrix": matrix, "resources": RESOURCES, "actions": ACTIONS,
            "granted": granted_count, "total": total,
            "coverage": round(granted_count / total * 100)}


def check_permission(grants: dict[str, list[str]], resource: str, action: str) -> bool:
    if resource not in RESOURCES or action not in ACTIONS:
        return False
    return action in grants.get(resource, [])
