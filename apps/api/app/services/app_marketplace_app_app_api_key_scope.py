"""API key scope — fine-grained scope management for API keys."""


AVAILABLE_SCOPES = {
    "apps:read": {"label": "Read Apps", "category": "apps", "risk": "low"},
    "apps:write": {"label": "Write Apps", "category": "apps", "risk": "medium"},
    "apps:delete": {"label": "Delete Apps", "category": "apps", "risk": "high"},
    "analytics:read": {"label": "Read Analytics", "category": "analytics", "risk": "low"},
    "webhooks:manage": {"label": "Manage Webhooks", "category": "webhooks", "risk": "medium"},
    "billing:read": {"label": "Read Billing", "category": "billing", "risk": "medium"},
    "billing:write": {"label": "Write Billing", "category": "billing", "risk": "high"},
    "admin:all": {"label": "Full Admin", "category": "admin", "risk": "critical"},
}


def validate_scopes(*, requested: list[str]) -> dict:
    valid = []
    invalid = []
    max_risk = "low"
    risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    for scope in requested:
        info = AVAILABLE_SCOPES.get(scope)
        if info:
            valid.append({"scope": scope, **info})
            if risk_order.get(info["risk"], 0) > risk_order.get(max_risk, 0):
                max_risk = info["risk"]
        else:
            invalid.append(scope)
    return {
        "valid_scopes": valid,
        "invalid_scopes": invalid,
        "all_valid": len(invalid) == 0,
        "max_risk": max_risk,
        "needs_approval": max_risk in ("high", "critical"),
        "scope_count": len(valid),
    }


def get_minimal_scopes(*, operations: list[str]) -> dict:
    op_map = {"list_apps": ["apps:read"], "create_app": ["apps:read", "apps:write"],
              "delete_app": ["apps:read", "apps:delete"], "view_analytics": ["analytics:read"],
              "manage_webhooks": ["webhooks:manage"]}
    scopes = set()
    for op in operations:
        scopes.update(op_map.get(op, []))
    return {"operations": operations, "minimal_scopes": sorted(scopes),
            "scope_count": len(scopes)}
