"""App gallery — curated collections and featured apps."""


def build_gallery(*, featured: list[dict], collections: list[dict],
                    trending: list[dict]) -> dict:
    return {
        "sections": [
            {"id": "featured", "title": "Featured Apps", "icon": "⭐",
             "apps": featured[:6]},
            {"id": "trending", "title": "Trending Now", "icon": "🔥",
             "apps": trending[:6]},
        ],
        "collections": [
            {"id": c["id"], "title": c["title"], "description": c.get("description", ""),
             "app_count": c.get("app_count", 0), "icon": c.get("icon", "📦")}
            for c in collections
        ],
        "total_featured": len(featured),
        "total_trending": len(trending),
        "total_collections": len(collections),
    }


def get_collection_detail(*, collection: dict, apps: list[dict]) -> dict:
    return {
        "id": collection["id"],
        "title": collection["title"],
        "description": collection.get("description", ""),
        "apps": apps,
        "app_count": len(apps),
        "curator": collection.get("curator", "OpenSkill Team"),
    }
