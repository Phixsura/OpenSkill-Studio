"""App permissions v2 — granular permission system with explanations and risk levels."""

PERMISSIONS = {
    "read:users": {"label": "Read user profiles", "risk": "low", "category": "users"},
    "write:users": {"label": "Modify user profiles", "risk": "medium", "category": "users"},
    "read:projects": {"label": "Read projects", "risk": "low", "category": "projects"},
    "write:projects": {"label": "Create/edit projects", "risk": "medium", "category": "projects"},
    "read:billing": {"label": "View billing info", "risk": "high", "category": "billing"},
    "admin:org": {"label": "Organization admin", "risk": "critical", "category": "admin"},
    "webhooks:manage": {"label": "Manage webhooks", "risk": "medium", "category": "integrations"},
    "secrets:read": {"label": "Read secrets", "risk": "critical", "category": "security"},
}


def get_permission_details(*, scopes: list[str]) -> list[dict]:
    return [{"scope": s, **PERMISSIONS.get(s, {"label": s, "risk": "unknown", "category": "other"})} for s in scopes]


def compute_risk_summary(*, scopes: list[str]) -> dict:
    details = get_permission_details(scopes=scopes)
    risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in details:
        risk_counts[d.get("risk", "unknown")] = risk_counts.get(d.get("risk", "unknown"), 0) + 1
    overall = "critical" if risk_counts["critical"] > 0 else "high" if risk_counts["high"] > 0 else "medium" if risk_counts["medium"] > 0 else "low"
    return {"overall_risk": overall, "risk_counts": risk_counts, "total_permissions": len(scopes),
            "requires_admin_review": overall in ("high", "critical")}


def group_by_category(*, scopes: list[str]) -> dict:
    groups: dict[str, list] = {}
    for s in scopes:
        info = PERMISSIONS.get(s, {"category": "other"})
        cat = info.get("category", "other")
        groups.setdefault(cat, []).append({"scope": s, **info})
    return groups
