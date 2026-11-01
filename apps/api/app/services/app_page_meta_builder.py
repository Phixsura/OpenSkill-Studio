"""App page meta builder — build complete page data for marketplace app detail."""

def build_app_page(*, app: dict, developer: dict, versions: list[dict], stats: dict, badges: list[dict]) -> dict:
    return {
        "app": app, "developer": developer,
        "latest_version": versions[0] if versions else None,
        "version_count": len(versions),
        "stats": stats, "badges": badges,
        "breadcrumbs": [{"label": "Marketplace", "href": "/marketplace"}, {"label": "Apps", "href": "/marketplace/apps"}, {"label": app.get("name", "")}],
    }
