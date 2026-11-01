"""App sidebar — app-level sidebar navigation for detail pages."""

import html

APP_NAV_ITEMS = [
    {"id": "overview", "label": "Overview", "icon": "📊", "href": "overview"},
    {"id": "analytics", "label": "Analytics", "icon": "📈", "href": "analytics"},
    {"id": "reviews", "label": "Reviews", "icon": "⭐", "href": "reviews"},
    {"id": "versions", "label": "Versions", "icon": "📦", "href": "versions"},
    {"id": "webhooks", "label": "Webhooks", "icon": "🔗", "href": "webhooks"},
    {"id": "settings", "label": "Settings", "icon": "⚙️", "href": "settings"},
]


def build_app_sidebar(*, app_id: str, app_name: str, active_section: str = "overview",
                         badges: dict[str, int] | None = None) -> dict:
    items = []
    for nav in APP_NAV_ITEMS:
        badge = (badges or {}).get(nav["id"])
        items.append({
            "id": nav["id"], "label": nav["label"], "icon": nav["icon"],
            "href": f"/apps/{app_id}/{nav['href']}",
            "active": nav["id"] == active_section,
            "badge": badge,
        })
    return {"app_name": html.escape(app_name), "app_id": app_id,
            "items": items, "active_section": active_section}
