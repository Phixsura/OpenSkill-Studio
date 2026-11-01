"""OAuth scope manager — define and validate OAuth scopes."""
from __future__ import annotations

SCOPES = {
    "read:user": {"description": "Read user profile", "category": "user"},
    "write:user": {"description": "Update user profile", "category": "user"},
    "read:apps": {"description": "List installed apps", "category": "apps"},
    "write:apps": {"description": "Install/uninstall apps", "category": "apps"},
    "read:billing": {"description": "View billing info", "category": "billing"},
    "write:billing": {"description": "Manage billing", "category": "billing"},
    "admin": {"description": "Full admin access", "category": "admin"},
    "read:analytics": {"description": "View analytics", "category": "analytics"},
}


def validate_scopes(requested: list[str]) -> dict:
    valid = [s for s in requested if s in SCOPES]
    invalid = [s for s in requested if s not in SCOPES]
    categories = sorted({SCOPES[s]["category"] for s in valid})
    return {"valid": valid, "invalid": invalid, "all_valid": len(invalid) == 0,
            "categories": categories, "has_admin": "admin" in valid}


def scope_diff(current: list[str], requested: list[str]) -> dict:
    cur = set(current)
    req = set(requested)
    added = sorted(req - cur)
    removed = sorted(cur - req)
    return {"added": added, "removed": removed, "unchanged": sorted(cur & req),
            "is_escalation": bool(added), "needs_reauth": bool(added)}


def list_scopes(category: str | None = None) -> list[dict]:
    items = []
    for scope, info in SCOPES.items():
        if category and info["category"] != category:
            continue
        items.append({"scope": scope, **info})
    return items
