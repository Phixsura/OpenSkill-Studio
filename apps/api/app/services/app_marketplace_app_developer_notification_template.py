"""Notification templates — predefined notification formats for common events."""

TEMPLATES = {
    "install": {"title": "New Installation", "body": "{app_name} was installed by {org_name}", "icon": "📥", "priority": "normal"},
    "uninstall": {"title": "App Uninstalled", "body": "{app_name} was uninstalled by {org_name}", "icon": "📤", "priority": "normal"},
    "review": {"title": "New Review", "body": "{reviewer} left a {rating}★ review on {app_name}", "icon": "⭐", "priority": "normal"},
    "error_spike": {"title": "Error Spike Detected", "body": "{app_name} error rate increased to {error_rate}%", "icon": "🚨", "priority": "urgent"},
    "version_approved": {"title": "Version Approved", "body": "{app_name} v{version} has been approved!", "icon": "✅", "priority": "normal"},
    "quota_warning": {"title": "Quota Warning", "body": "{resource} usage at {usage_pct}% of limit", "icon": "⚠️", "priority": "high"},
}

def render_notification(*, template_id: str, params: dict) -> dict | None:
    tmpl = TEMPLATES.get(template_id)
    if not tmpl:
        return None
    try:
        body = tmpl["body"].format(**params)
    except KeyError:
        body = tmpl["body"]
    return {"title": tmpl["title"], "body": body, "icon": tmpl["icon"], "priority": tmpl["priority"]}

def list_templates() -> list[dict]:
    return [{"id": k, "title": v["title"], "priority": v["priority"]} for k, v in TEMPLATES.items()]
