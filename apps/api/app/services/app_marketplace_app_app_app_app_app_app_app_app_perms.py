"""App permissions checker — validate app-requested permissions against user grants."""
from __future__ import annotations

AVAILABLE_PERMISSIONS = {
    "read:profile": {"label": "Read Profile", "description": "Access your name and email", "risk": "low"},
    "write:profile": {"label": "Write Profile", "description": "Update your profile", "risk": "medium"},
    "read:apps": {"label": "Read Apps", "description": "List your applications", "risk": "low"},
    "write:apps": {"label": "Manage Apps", "description": "Create and update apps", "risk": "high"},
    "read:analytics": {"label": "Read Analytics", "description": "View usage data", "risk": "low"},
    "admin:org": {"label": "Org Admin", "description": "Full organization access", "risk": "critical"},
    "deploy": {"label": "Deploy", "description": "Deploy to environments", "risk": "high"},
    "billing:read": {"label": "View Billing", "description": "View invoices", "risk": "medium"},
}


def check_permissions(*, requested: list[str], granted: list[str]) -> dict:
    allowed = [p for p in requested if p in granted]
    denied = [p for p in requested if p not in granted]
    details = []
    for p in requested:
        info = AVAILABLE_PERMISSIONS.get(p, {"label": p, "risk": "unknown"})
        details.append({"permission": p, "label": info.get("label", p),
                         "risk": info.get("risk", "unknown"),
                         "granted": p in granted})
    return {"all_granted": len(denied) == 0, "allowed": allowed,
            "denied": denied, "details": details}


def classify_risk(permissions: list[str]) -> dict:
    risks = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for p in permissions:
        info = AVAILABLE_PERMISSIONS.get(p, {})
        risk = info.get("risk", "unknown")
        if risk in risks:
            risks[risk] += 1
    max_risk = "critical" if risks["critical"] else "high" if risks["high"] else \
               "medium" if risks["medium"] else "low"
    return {"risks": risks, "max_risk": max_risk, "total": len(permissions)}
