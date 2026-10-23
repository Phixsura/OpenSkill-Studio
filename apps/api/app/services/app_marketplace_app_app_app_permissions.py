"""App permissions — permission request and approval management."""

import html

PERMISSION_CATALOG = {
    "read:profile": {"label": "Read Profile", "description": "Access user's name and email", "risk": "low", "icon": "👤"},
    "read:apps": {"label": "Read Apps", "description": "View installed apps", "risk": "low", "icon": "📦"},
    "write:apps": {"label": "Manage Apps", "description": "Create and modify apps", "risk": "medium", "icon": "✏️"},
    "read:analytics": {"label": "Read Analytics", "description": "View usage analytics", "risk": "low", "icon": "📊"},
    "write:webhooks": {"label": "Manage Webhooks", "description": "Create and manage webhooks", "risk": "medium", "icon": "🔗"},
    "admin:org": {"label": "Org Admin", "description": "Full organization admin access", "risk": "high", "icon": "🏢"},
    "write:billing": {"label": "Manage Billing", "description": "View and manage billing", "risk": "high", "icon": "💳"},
}


def build_permission_request(*, requested: list[str]) -> dict:
    items = []
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    for perm_id in requested:
        info = PERMISSION_CATALOG.get(perm_id)
        if not info:
            continue
        risk = info["risk"]
        risk_counts[risk] += 1
        items.append({"id": perm_id, **info})
    max_risk = "high" if risk_counts["high"] else "medium" if risk_counts["medium"] else "low"
    return {"permissions": items, "total": len(items), "risk_summary": risk_counts,
            "max_risk": max_risk, "requires_admin": risk_counts["high"] > 0}
