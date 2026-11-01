"""Complete app detail page — the ultimate aggregator for a marketplace app listing."""


def build_complete_app_detail_page(*, app: dict, developer: dict, versions: list[dict],
                                      reviews: dict, install_stats: dict, screenshots: list[dict],
                                      related_apps: list[dict], documentation: list[dict]) -> dict:
    return {
        "page_type": "app_detail",
        "app": {
            "id": app["id"], "name": app["name"], "slug": app.get("slug"),
            "description": app.get("description"), "category": app.get("category"),
            "status": app.get("status"),
        },
        "developer": {
            "name": developer.get("display_name"), "slug": developer.get("slug"),
            "verified": developer.get("verified", False),
        },
        "current_version": versions[0] if versions else None,
        "version_count": len(versions),
        "reviews_summary": reviews,
        "install_stats": install_stats,
        "screenshots": screenshots[:10],
        "related_apps": related_apps[:6],
        "documentation_pages": len(documentation),
        "tabs": ["overview", "reviews", "changelog", "documentation", "support"],
    }
