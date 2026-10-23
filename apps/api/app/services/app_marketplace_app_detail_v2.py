"""App detail v2 — comprehensive app detail page with all sections."""


def build_app_detail_v2(*, app: dict, developer: dict, version: dict | None,
                           reviews: dict, install_stats: dict, screenshots: list[dict],
                           related: list[dict], changelog: list[dict], pricing: dict | None) -> dict:
    return {
        "page_type": "app_detail_v2",
        "app": {"id": app["id"], "name": app["name"], "slug": app.get("slug"),
                "description": app.get("description", ""), "category": app.get("category")},
        "developer": {"name": developer.get("display_name"), "verified": developer.get("verified", False)},
        "version": version,
        "tabs": [
            {"key": "overview", "label": "Overview"},
            {"key": "reviews", "label": f"Reviews ({reviews.get('count', 0)})"},
            {"key": "changelog", "label": f"Changelog ({len(changelog)})"},
            {"key": "pricing", "label": "Pricing"} if pricing else None,
            {"key": "support", "label": "Support"},
        ],
        "sidebar": {
            "install_button": {"label": "Install", "action": "install"},
            "stats": install_stats,
            "screenshots": screenshots[:6],
            "related_apps": related[:4],
        },
        "seo": {"title": f"{app['name']} | OpenSkill Marketplace"},
    }


def get_app_detail_breadcrumb(*, app: dict) -> list[dict]:
    crumbs = [{"label": "Marketplace", "url": "/marketplace"}]
    if app.get("category"):
        crumbs.append({"label": app["category"].title(), "url": f"/marketplace/category/{app['category']}"})
    crumbs.append({"label": app["name"], "url": f"/marketplace/apps/{app.get('slug', app['id'])}"})
    return crumbs
