"""Portal page registry — registry of all developer portal pages."""

PORTAL_PAGES = [
    {"key": "overview", "title": "Overview", "path": "/dashboard/developer"},
    {"key": "apps", "title": "My Apps", "path": "/dashboard/developer/apps"},
    {"key": "keys", "title": "API Keys", "path": "/dashboard/developer/keys"},
    {"key": "settings", "title": "Settings", "path": "/dashboard/developer/settings"},
    {"key": "docs", "title": "Documentation", "path": "/dashboard/developer/docs"},
    {"key": "tutorial", "title": "Tutorial", "path": "/dashboard/developer/tutorial"},
    {"key": "api-reference", "title": "API Reference", "path": "/dashboard/developer/api-reference"},
]


def get_page(key: str) -> dict | None:
    return next((p for p in PORTAL_PAGES if p["key"] == key), None)


def get_all_pages() -> list[dict]:
    return PORTAL_PAGES
