"""Developer portal sitemap — navigation structure for the dev portal."""

PORTAL_PAGES = [
    {"path": "/developer", "title": "Dashboard", "icon": "📊"},
    {"path": "/developer/apps", "title": "My Apps", "icon": "📦"},
    {"path": "/developer/analytics", "title": "Analytics", "icon": "📈"},
    {"path": "/developer/webhooks", "title": "Webhooks", "icon": "🔗"},
    {"path": "/developer/sandbox", "title": "Sandbox", "icon": "🧪"},
    {"path": "/developer/team", "title": "Team", "icon": "👥"},
    {"path": "/developer/billing", "title": "Billing", "icon": "💳"},
    {"path": "/developer/settings", "title": "Settings", "icon": "⚙️"},
    {"path": "/developer/docs", "title": "Documentation", "icon": "📚"},
    {"path": "/developer/support", "title": "Support", "icon": "💬"},
]

def get_portal_navigation() -> list[dict]:
    return PORTAL_PAGES

def get_breadcrumb(*, path: str) -> list[dict]:
    crumbs = [{"path": "/developer", "title": "Developer Portal"}]
    page = next((p for p in PORTAL_PAGES if p["path"] == path), None)
    if page and page["path"] != "/developer":
        crumbs.append({"path": page["path"], "title": page["title"]})
    return crumbs
