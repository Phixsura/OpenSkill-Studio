"""Complete platform overview — the ULTIMATE master aggregator for the entire developer platform."""


def build_complete_platform_overview(*, platform_stats: dict, trending_apps: list[dict],
                                        recent_updates: list[dict], top_developers: list[dict],
                                        categories: list[dict], announcements: list[dict]) -> dict:
    return {
        "page_type": "platform_overview",
        "stats": {
            "total_apps": platform_stats.get("total_apps", 0),
            "total_developers": platform_stats.get("total_developers", 0),
            "total_installs": platform_stats.get("total_installs", 0),
            "apps_published_this_month": platform_stats.get("monthly_published", 0),
        },
        "sections": [
            {"key": "trending", "title": "Trending Apps", "data": trending_apps[:8]},
            {"key": "updates", "title": "Recent Updates", "data": recent_updates[:10]},
            {"key": "developers", "title": "Top Developers", "data": top_developers[:10]},
            {"key": "categories", "title": "Categories", "data": categories},
            {"key": "announcements", "title": "Announcements", "data": announcements[:3]},
        ],
        "links": {
            "docs": "/docs/developer",
            "api_reference": "/docs/api",
            "community": "/community",
            "status": "/status",
        },
    }
