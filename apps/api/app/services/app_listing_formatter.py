"""App listing formatter — prepare app data for marketplace display."""


def format_listing(app: dict, *, developer: dict | None = None, stats: dict | None = None) -> dict:
    """Format an app for marketplace listing display."""
    return {
        "id": app.get("id"),
        "name": app.get("name"),
        "slug": app.get("slug"),
        "description": app.get("description"),
        "icon_url": app.get("icon_url"),
        "category": app.get("category"),
        "developer_name": developer.get("display_name") if developer else None,
        "developer_verified": developer.get("verified", False) if developer else False,
        "install_count": stats.get("active_installs", 0) if stats else 0,
        "health_score": stats.get("health_score", 100) if stats else 100,
        "rating": stats.get("rating", 0) if stats else 0,
        "rating_count": stats.get("rating_count", 0) if stats else 0,
    }


def format_listings(apps: list[dict], *, developers: dict[str, dict] | None = None) -> list[dict]:
    """Format multiple apps for marketplace listing."""
    devs = developers or {}
    return [format_listing(app, developer=devs.get(app.get("developer_id", ""))) for app in apps]
