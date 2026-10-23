"""Permission scanner — analyze and report app permission usage."""


PERMISSION_DESCRIPTIONS = {
    "read_profile": {"label": "Read Profile", "risk": "low", "reason": "Access basic user info"},
    "write_data": {"label": "Write Data", "risk": "medium", "reason": "Create and modify data"},
    "read_contacts": {"label": "Read Contacts", "risk": "high", "reason": "Access user's contact list"},
    "send_notifications": {"label": "Send Notifications", "risk": "low", "reason": "Push notifications"},
    "access_billing": {"label": "Access Billing", "risk": "critical", "reason": "View payment info"},
    "admin_org": {"label": "Admin Organization", "risk": "critical", "reason": "Manage org settings"},
    "read_analytics": {"label": "Read Analytics", "risk": "medium", "reason": "View usage data"},
}


def scan_permissions(*, requested: list[str]) -> dict:
    results = []
    for perm in requested:
        info = PERMISSION_DESCRIPTIONS.get(perm)
        if info:
            results.append({"permission": perm, **info, "known": True})
        else:
            results.append({"permission": perm, "label": perm, "risk": "unknown",
                           "reason": "Undocumented permission", "known": False})
    risk_counts = {}
    for r in results:
        risk_counts[r["risk"]] = risk_counts.get(r["risk"], 0) + 1
    max_risk = "low"
    for level in ["unknown", "critical", "high", "medium"]:
        if risk_counts.get(level, 0) > 0:
            max_risk = level
            break
    return {"permissions": results, "total": len(results),
            "risk_summary": risk_counts, "max_risk": max_risk,
            "safe_to_install": max_risk in ("low", "medium")}
