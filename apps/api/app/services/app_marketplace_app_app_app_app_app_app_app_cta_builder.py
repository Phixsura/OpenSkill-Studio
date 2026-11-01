"""CTA builder — contextual call-to-action for different user states."""
from __future__ import annotations

CTAS = {
    "new_user": {"title": "Start Building", "subtitle": "Create your first app in minutes",
                  "button": "Get Started", "icon": "🚀", "variant": "primary"},
    "no_apps": {"title": "Create Your First App", "subtitle": "Ship an integration to the marketplace",
                 "button": "Create App", "icon": "📱", "variant": "primary"},
    "no_key": {"title": "Generate API Key", "subtitle": "Authenticate your API requests",
                "button": "Generate Key", "icon": "🔑", "variant": "secondary"},
    "upgrade": {"title": "Upgrade Your Plan", "subtitle": "Unlock advanced features and higher limits",
                 "button": "View Plans", "icon": "⬆️", "variant": "primary"},
    "invite": {"title": "Invite Your Team", "subtitle": "Collaborate with teammates",
                "button": "Invite", "icon": "👥", "variant": "secondary"},
}


def get_cta(state: str) -> dict:
    return CTAS.get(state, CTAS["new_user"])


def get_next_cta(*, has_app: bool, has_key: bool, has_team: bool, plan: str) -> dict:
    if not has_app:
        return get_cta("no_apps")
    if not has_key:
        return get_cta("no_key")
    if plan == "free":
        return get_cta("upgrade")
    if not has_team:
        return get_cta("invite")
    return get_cta("new_user")
