"""Collection v2 — curated app collections with dynamic and manual curation."""


def create_collection_v2(*, title: str, description: str, slug: str,
                            apps: list[dict], curator_id: str, collection_type: str = "manual") -> dict:
    valid_types = {"manual", "trending", "category_best", "new_arrivals", "editorial"}
    if collection_type not in valid_types:
        return {"error": f"Invalid type. Use: {', '.join(sorted(valid_types))}"}
    return {"title": title, "description": description, "slug": slug,
            "app_ids": [a["id"] for a in apps], "app_count": len(apps),
            "curator_id": curator_id, "collection_type": collection_type,
            "status": "published" if len(apps) >= 3 else "draft", "error": None}


def build_collection_page(*, collection: dict, apps: list[dict], related: list[dict]) -> dict:
    return {
        "collection": collection, "apps": apps,
        "related_collections": related[:4],
        "seo": {"title": f"{collection['title']} | OpenSkill Marketplace",
                "description": collection.get("description", "")[:160]},
    }


def auto_curate_collection(*, apps: list[dict], criteria: str, limit: int = 10) -> list[dict]:
    if criteria == "trending":
        return sorted(apps, key=lambda a: -a.get("trending_score", 0))[:limit]
    elif criteria == "top_rated":
        return sorted(apps, key=lambda a: -a.get("avg_rating", 0))[:limit]
    elif criteria == "newest":
        return sorted(apps, key=lambda a: a.get("created_at", ""), reverse=True)[:limit]
    return apps[:limit]
