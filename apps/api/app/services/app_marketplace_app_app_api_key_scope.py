"""API key scope — fine-grained API key permission management."""

import html

SCOPES = {
    "apps:read": {"description": "Read app data", "category": "Apps", "risk": "low"},
    "apps:write": {"description": "Create and update apps", "category": "Apps", "risk": "medium"},
    "apps:delete": {"description": "Delete apps", "category": "Apps", "risk": "high"},
    "webhooks:manage": {"description": "Manage webhooks", "category": "Webhooks", "risk": "medium"},
    "analytics:read": {"description": "View analytics", "category": "Analytics", "risk": "low"},
    "users:read": {"description": "Read user info", "category": "Users", "risk": "low"},
    "billing:read": {"description": "View billing", "category": "Billing", "risk": "medium"},
    "billing:write": {"description": "Manage billing", "category": "Billing", "risk": "high"},
}


def build_scope_selector(*, granted: list[str]) -> dict:
    granted_set = set(granted)
    categories: dict[str, list] = {}
    for sid, info in SCOPES.items():
        cat = info["category"]
        categories.setdefault(cat, []).append({
            "id": sid, "description": info["description"],
            "risk": info["risk"], "granted": sid in granted_set,
        })
    total_granted = len(granted_set & set(SCOPES.keys()))
    has_high_risk = any(SCOPES.get(s, {}).get("risk") == "high" for s in granted)
    return {"categories": categories, "total_scopes": len(SCOPES),
            "granted": total_granted, "has_high_risk": has_high_risk}
