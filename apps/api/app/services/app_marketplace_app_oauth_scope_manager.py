"""OAuth scope manager — define and validate OAuth permission scopes."""


SCOPES = {
    "read:profile": {"description": "Read user profile", "category": "user", "risk": "low"},
    "write:profile": {"description": "Update user profile", "category": "user", "risk": "medium"},
    "read:apps": {"description": "List installed apps", "category": "apps", "risk": "low"},
    "write:apps": {"description": "Install/uninstall apps", "category": "apps", "risk": "high"},
    "read:analytics": {"description": "View analytics data", "category": "analytics", "risk": "medium"},
    "admin:org": {"description": "Manage organization", "category": "admin", "risk": "critical"},
    "webhook:manage": {"description": "Create/delete webhooks", "category": "webhooks", "risk": "medium"},
}


def validate_scopes(*, requested: list[str]) -> dict:
    valid = []
    invalid = []
    for scope in requested:
        if scope in SCOPES:
            valid.append({"scope": scope, **SCOPES[scope]})
        else:
            invalid.append(scope)
    max_risk = "low"
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    for v in valid:
        if risk_order.get(v["risk"], 0) > risk_order.get(max_risk, 0):
            max_risk = v["risk"]
    return {
        "valid_scopes": valid,
        "invalid_scopes": invalid,
        "all_valid": len(invalid) == 0,
        "max_risk": max_risk,
        "requires_admin_consent": max_risk in ("high", "critical"),
    }


def group_scopes_by_category(*, scopes: list[str]) -> dict:
    groups: dict[str, list] = {}
    for scope in scopes:
        info = SCOPES.get(scope)
        if info:
            cat = info["category"]
            groups.setdefault(cat, []).append({"scope": scope, **info})
    return {"groups": [{"category": k, "scopes": v} for k, v in sorted(groups.items())],
            "category_count": len(groups)}
