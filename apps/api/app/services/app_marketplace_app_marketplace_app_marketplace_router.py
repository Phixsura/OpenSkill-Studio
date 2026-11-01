"""Marketplace router — URL routing configuration for all marketplace pages."""

ROUTES = [
    {"path": "/marketplace", "page": "home", "title": "Marketplace", "auth_required": False},
    {"path": "/marketplace/search", "page": "search", "title": "Search", "auth_required": False},
    {"path": "/marketplace/category/:id", "page": "category", "title": "Category", "auth_required": False},
    {"path": "/marketplace/collections", "page": "collections", "title": "Collections", "auth_required": False},
    {"path": "/marketplace/collections/:slug", "page": "collection_detail", "title": "Collection", "auth_required": False},
    {"path": "/marketplace/apps/:slug", "page": "app_detail", "title": "App Detail", "auth_required": False},
    {"path": "/marketplace/apps/:slug/reviews", "page": "app_reviews", "title": "Reviews", "auth_required": False},
    {"path": "/marketplace/apps/:slug/changelog", "page": "app_changelog", "title": "Changelog", "auth_required": False},
    {"path": "/marketplace/developers/:slug", "page": "developer_profile", "title": "Developer", "auth_required": False},
    {"path": "/marketplace/compare", "page": "compare", "title": "Compare Apps", "auth_required": False},
    {"path": "/marketplace/installed", "page": "installed_apps", "title": "My Apps", "auth_required": True},
    {"path": "/developer", "page": "developer_dashboard", "title": "Dashboard", "auth_required": True},
    {"path": "/developer/apps", "page": "developer_apps", "title": "My Apps", "auth_required": True},
    {"path": "/developer/apps/new", "page": "create_app", "title": "Create App", "auth_required": True},
    {"path": "/developer/apps/:id", "page": "app_manage", "title": "Manage App", "auth_required": True},
    {"path": "/developer/apps/:id/settings", "page": "app_settings", "title": "Settings", "auth_required": True},
    {"path": "/developer/apps/:id/analytics", "page": "app_analytics", "title": "Analytics", "auth_required": True},
    {"path": "/developer/apps/:id/webhooks", "page": "app_webhooks", "title": "Webhooks", "auth_required": True},
    {"path": "/developer/analytics", "page": "developer_analytics", "title": "Analytics", "auth_required": True},
    {"path": "/developer/team", "page": "developer_team", "title": "Team", "auth_required": True},
    {"path": "/developer/billing", "page": "developer_billing", "title": "Billing", "auth_required": True},
    {"path": "/developer/settings", "page": "developer_settings", "title": "Settings", "auth_required": True},
]


def get_all_routes() -> list[dict]:
    return ROUTES


def get_public_routes() -> list[dict]:
    return [r for r in ROUTES if not r["auth_required"]]


def get_protected_routes() -> list[dict]:
    return [r for r in ROUTES if r["auth_required"]]


def match_route(*, path: str) -> dict | None:
    import re
    for route in ROUTES:
        pattern = re.sub(r':(\w+)', r'[^/]+', route["path"])
        if re.match(f'^{pattern}$', path):
            return route
    return None


def build_sitemap_urls(*, base_url: str = "https://openskill.dev") -> list[str]:
    return [f"{base_url}{r['path']}" for r in ROUTES if not r["auth_required"] and ":" not in r["path"]]
