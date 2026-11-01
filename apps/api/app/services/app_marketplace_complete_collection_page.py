"""Complete collection page — full collection detail with apps, curator info, and related."""


def build_complete_collection_page(*, collection: dict, apps: list[dict],
                                       curator: dict, related_collections: list[dict]) -> dict:
    return {
        "page_type": "collection_detail",
        "collection": {"title": collection["title"], "slug": collection.get("slug"),
                         "description": collection.get("description", ""),
                         "type": collection.get("type", "manual"), "app_count": len(apps)},
        "curator": {"name": curator.get("display_name"), "slug": curator.get("slug"),
                      "verified": curator.get("verified", False)},
        "apps": apps, "app_count": len(apps),
        "related": related_collections[:4],
        "seo": {"title": f"{collection['title']} — OpenSkill Marketplace",
                "description": collection.get("description", "")[:160]},
    }
