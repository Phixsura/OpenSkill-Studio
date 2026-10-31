"""Marketplace homepage — the complete marketplace landing page aggregator."""


def build_marketplace_homepage(*, featured_apps: list[dict], trending_apps: list[dict],
                                  categories: list[dict], stats: dict,
                                  announcements: list[dict]) -> dict:
    return {
        "hero": {
            "title": "OpenSkill Marketplace",
            "subtitle": "Discover, install, and build amazing apps",
            "cta": "Explore Apps",
            "app_count": stats.get("total_apps", 0),
            "developer_count": stats.get("total_developers", 0),
        },
        "featured": {
            "title": "Featured Apps",
            "apps": featured_apps[:6],
        },
        "trending": {
            "title": "Trending Now",
            "apps": trending_apps[:6],
        },
        "categories": {
            "title": "Browse Categories",
            "items": categories[:12],
        },
        "stats": {
            "total_apps": stats.get("total_apps", 0),
            "total_developers": stats.get("total_developers", 0),
            "total_installs": stats.get("total_installs", 0),
            "avg_rating": stats.get("avg_rating", 0),
        },
        "announcements": announcements[:3],
        "sections_count": 5,
    }
