"""Notification center — build developer notification feed."""

from datetime import datetime, timezone


def build_notification(*, type: str, title: str, message: str, app_id: str | None = None,
                         action_url: str | None = None) -> dict:
    return {
        "type": type, "title": title, "message": message,
        "app_id": app_id, "action_url": action_url,
        "read": False, "created_at": datetime.now(timezone.utc).isoformat(),
    }


NOTIFICATION_TEMPLATES = {
    "new_install": {"title": "New Installation", "template": "{app_name} was installed by {org_name}"},
    "new_review": {"title": "New Review", "template": "{reviewer} left a {rating}★ review on {app_name}"},
    "version_approved": {"title": "Version Approved", "template": "{app_name} v{version} has been approved"},
    "version_rejected": {"title": "Version Rejected", "template": "{app_name} v{version} was rejected: {reason}"},
    "security_alert": {"title": "Security Alert", "template": "Vulnerability found in {app_name}: {issue}"},
}


def create_from_template(*, type: str, params: dict) -> dict | None:
    tmpl = NOTIFICATION_TEMPLATES.get(type)
    if not tmpl:
        return None
    try:
        message = tmpl["template"].format(**params)
    except KeyError:
        message = tmpl["template"]
    return build_notification(type=type, title=tmpl["title"], message=message,
                               app_id=params.get("app_id"), action_url=params.get("action_url"))


def get_unread_count(*, notifications: list[dict]) -> int:
    return sum(1 for n in notifications if not n.get("read"))


def mark_all_read(*, notifications: list[dict]) -> list[dict]:
    return [{**n, "read": True} for n in notifications]
