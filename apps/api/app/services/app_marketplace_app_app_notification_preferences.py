"""Notification preferences — channel-specific notification settings."""

import html

CHANNELS = {
    "email": {"label": "Email", "icon": "📧"},
    "push": {"label": "Push", "icon": "📱"},
    "slack": {"label": "Slack", "icon": "💬"},
    "webhook": {"label": "Webhook", "icon": "🔗"},
}

EVENT_TYPES = [
    {"id": "app_installed", "label": "App Installed", "category": "Apps"},
    {"id": "app_reviewed", "label": "New Review", "category": "Apps"},
    {"id": "deploy_success", "label": "Deploy Success", "category": "Deploys"},
    {"id": "deploy_failed", "label": "Deploy Failed", "category": "Deploys"},
    {"id": "security_alert", "label": "Security Alert", "category": "Security"},
    {"id": "billing_invoice", "label": "New Invoice", "category": "Billing"},
]


def build_preferences(*, current: dict[str, dict[str, bool]] | None = None) -> dict:
    defaults = {e["id"]: {c: True for c in CHANNELS} for e in EVENT_TYPES}
    if current:
        for event_id, channels in current.items():
            if event_id in defaults:
                defaults[event_id].update(channels)
    items = []
    for et in EVENT_TYPES:
        items.append({**et, "channels": defaults[et["id"]]})
    categories = sorted(set(e["category"] for e in EVENT_TYPES))
    return {"events": items, "channels": list(CHANNELS.values()),
            "categories": categories, "total_events": len(items)}
