"""App detail page builder — compile all data for marketplace app detail page."""


def build_detail_page(*, app: dict, developer: dict, versions: list[dict], stats: dict,
                        health: dict, badges: list[dict], reviews: dict, related: list[dict]) -> dict:
    return {
        "app": app, "developer": developer,
        "latest_version": versions[0] if versions else None,
        "version_count": len(versions),
        "stats": stats, "health": health,
        "badges": badges, "reviews": reviews,
        "related_apps": related[:5],
        "breadcrumbs": [
            {"label": "Marketplace", "href": "/marketplace"},
            {"label": app.get("category", "").replace("_", " ").title(), "href": f"/marketplace/apps?category={app.get('category')}"},
            {"label": app.get("name", "")},
        ],
    }
