"""Token scope — OAuth scope definition and validation."""

import html

SCOPES = {
    "read:apps": {"description": "Read app data", "category": "Apps"},
    "write:apps": {"description": "Create and update apps", "category": "Apps"},
    "delete:apps": {"description": "Delete apps", "category": "Apps", "dangerous": True},
    "read:analytics": {"description": "Read analytics data", "category": "Analytics"},
    "read:users": {"description": "Read user profiles", "category": "Users"},
    "write:webhooks": {"description": "Manage webhooks", "category": "Webhooks"},
    "admin": {"description": "Full admin access", "category": "Admin", "dangerous": True},
}


def validate_scopes(*, requested: list[str]) -> dict:
    valid = []
    invalid = []
    dangerous = []
    for s in requested:
        if s in SCOPES:
            valid.append(s)
            if SCOPES[s].get("dangerous"):
                dangerous.append(s)
        else:
            invalid.append(s)
    return {"valid": valid, "invalid": invalid, "dangerous": dangerous,
            "all_valid": len(invalid) == 0, "has_dangerous": len(dangerous) > 0}


def list_scopes(*, category: str | None = None) -> dict:
    items = []
    for scope_id, info in SCOPES.items():
        if category and info["category"] != category:
            continue
        items.append({"id": scope_id, "description": html.escape(info["description"]),
                       "category": info["category"],
                       "dangerous": info.get("dangerous", False)})
    categories = sorted(set(s["category"] for s in SCOPES.values()))
    return {"scopes": items, "total": len(items), "categories": categories}
