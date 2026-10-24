"""Notification formatter — format platform notifications for different channels."""

TEMPLATES = {
    "app.installed": "📦 {app_name} was installed in {org_name}",
    "app.uninstalled": "🗑️ {app_name} was uninstalled from {org_name}",
    "review.submitted": "📝 {app_name} v{version} submitted for review",
    "review.approved": "✅ {app_name} v{version} approved",
    "review.rejected": "❌ {app_name} v{version} rejected",
    "app.revoked": "🚫 {app_name} has been revoked",
    "version.published": "🚀 {app_name} v{version} published",
}


def format_notification(event_type: str, **kwargs) -> str:
    template = TEMPLATES.get(event_type)
    if not template:
        return f"Event: {event_type}"
    try:
        return template.format(**kwargs)
    except KeyError:
        return template.format_map({**{k: "?" for k in ("app_name", "org_name", "version")}, **kwargs})


def get_notification_icon(event_type: str) -> str:
    icons = {"app.installed": "📦", "app.uninstalled": "🗑️", "review.submitted": "📝",
             "review.approved": "✅", "review.rejected": "❌", "app.revoked": "🚫", "version.published": "🚀"}
    return icons.get(event_type, "🔔")
