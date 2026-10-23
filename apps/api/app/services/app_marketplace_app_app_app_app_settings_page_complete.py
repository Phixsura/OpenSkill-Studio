"""App settings page complete — all settings sections in one view."""

import html

SETTINGS_TABS = [
    {"id": "general", "label": "General", "icon": "⚙️"},
    {"id": "visibility", "label": "Visibility", "icon": "👁️"},
    {"id": "webhooks", "label": "Webhooks", "icon": "🔗"},
    {"id": "api_keys", "label": "API Keys", "icon": "🔑"},
    {"id": "collaborators", "label": "Collaborators", "icon": "👥"},
    {"id": "security", "label": "Security", "icon": "🔒"},
    {"id": "notifications", "label": "Notifications", "icon": "🔔"},
    {"id": "danger", "label": "Danger Zone", "icon": "⚠️"},
]


def build_settings_page_complete(*, app: dict, active_tab: str = "general") -> dict:
    tabs = [{"id": t["id"], "label": t["label"], "icon": t["icon"],
             "active": t["id"] == active_tab} for t in SETTINGS_TABS]
    return {
        "app_name": html.escape(app.get("name", "")),
        "app_id": app.get("id", ""),
        "version": app.get("version", "1.0.0"),
        "tabs": tabs,
        "active_tab": active_tab,
        "tab_count": len(tabs),
    }
