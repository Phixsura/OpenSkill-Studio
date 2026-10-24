"""Empty state manager — contextual empty states with CTAs for every platform section."""
from __future__ import annotations

EMPTY_STATES = {
    "apps": {"icon": "📱", "title": "No apps yet", "description": "Create your first app to get started.", "cta": "Create App", "cta_url": "/apps/new"},
    "webhooks": {"icon": "🔗", "title": "No webhooks configured", "description": "Set up webhooks to receive real-time events.", "cta": "Add Webhook", "cta_url": "/webhooks/new"},
    "api_keys": {"icon": "🔑", "title": "No API keys", "description": "Generate a key to authenticate API requests.", "cta": "Generate Key", "cta_url": "/settings/keys"},
    "deployments": {"icon": "🚀", "title": "No deployments", "description": "Deploy your first version to get started.", "cta": "Deploy", "cta_url": "/deploy"},
    "team": {"icon": "👥", "title": "Just you so far", "description": "Invite teammates to collaborate.", "cta": "Invite", "cta_url": "/team/invite"},
    "logs": {"icon": "📋", "title": "No logs yet", "description": "Logs will appear once your app starts receiving traffic.", "cta": None, "cta_url": None},
    "analytics": {"icon": "📊", "title": "No data yet", "description": "Analytics will populate as users interact with your app.", "cta": None, "cta_url": None},
}


def get_empty_state(section: str) -> dict:
    state = EMPTY_STATES.get(section)
    if not state:
        return {"icon": "📭", "title": "Nothing here", "description": "This section is empty.", "cta": None, "cta_url": None}
    return dict(state)


def list_sections() -> list[str]:
    return sorted(EMPTY_STATES.keys())
