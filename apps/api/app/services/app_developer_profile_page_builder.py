"""Developer profile page builder — compile public developer profile data."""

def build_developer_profile_page(*, developer: dict, apps: list[dict], stats: dict) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    categories = sorted(set(a.get("category", "") for a in published))
    return {
        "developer": developer,
        "published_apps": published,
        "app_count": len(published),
        "categories": categories,
        "total_installs": stats.get("total_installs", sum(a.get("install_count", 0) for a in published)),
        "avg_health": stats.get("avg_health", 100),
        "verified": developer.get("verified", False),
        "breadcrumbs": [{"label": "Marketplace", "href": "/marketplace"}, {"label": "Developers", "href": "/marketplace/developers"}, {"label": developer.get("display_name", "")}],
    }
