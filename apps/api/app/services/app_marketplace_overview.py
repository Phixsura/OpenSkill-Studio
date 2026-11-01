"""Marketplace overview — build the marketplace home page data."""


def build_marketplace_overview(*, featured: list[dict], trending: list[dict], recent: list[dict],
                                 categories: list[dict], stats: dict) -> dict:
    return {
        "featured": featured[:6],
        "trending": trending[:10],
        "recent": recent[:12],
        "categories": categories,
        "stats": stats,
        "sections": [
            {"title": "Featured Apps", "type": "featured", "count": len(featured[:6])},
            {"title": "Trending", "type": "trending", "count": len(trending[:10])},
            {"title": "Recently Added", "type": "recent", "count": len(recent[:12])},
        ],
    }
