"""Complete marketplace home — master aggregator for the marketplace landing page."""


def build_complete_marketplace_home(*, featured_apps: list[dict], trending_apps: list[dict],
                                       new_apps: list[dict], categories: list[dict],
                                       collections: list[dict], stats: dict) -> dict:
    return {
        "page_type": "marketplace_home",
        "hero": {
            "title": "OpenSkill Marketplace",
            "subtitle": f"Discover {stats.get('total_apps', 0)} apps from {stats.get('total_developers', 0)} developers",
        },
        "sections": [
            {"key": "featured", "title": "Featured Apps", "apps": featured_apps[:6]},
            {"key": "trending", "title": "Trending This Week", "apps": trending_apps[:8]},
            {"key": "new", "title": "Recently Added", "apps": new_apps[:8]},
            {"key": "categories", "title": "Browse by Category", "categories": categories},
            {"key": "collections", "title": "Curated Collections", "collections": collections[:4]},
        ],
        "stats": stats,
    }
