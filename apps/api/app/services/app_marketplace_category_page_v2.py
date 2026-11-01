"""Category page v2 — complete category browsing page with subcategories and filters."""


def build_category_page_v2(*, category: dict, apps: list[dict], subcategories: list[dict],
                               page: int = 1, per_page: int = 24, sort_by: str = "popular",
                               filters: dict | None = None) -> dict:
    # Sort
    if sort_by == "popular":
        apps = sorted(apps, key=lambda a: -a.get("install_count", 0))
    elif sort_by == "rating":
        apps = sorted(apps, key=lambda a: -a.get("avg_rating", 0))
    elif sort_by == "newest":
        apps = sorted(apps, key=lambda a: a.get("created_at", ""), reverse=True)

    total = len(apps)
    start = (page - 1) * per_page
    page_apps = apps[start:start + per_page]
    total_pages = max(1, (total + per_page - 1) // per_page)

    return {
        "page_type": "category_v2",
        "category": {"id": category.get("id"), "name": category.get("name"),
                       "icon": category.get("icon"), "description": category.get("description", "")},
        "subcategories": subcategories,
        "apps": page_apps,
        "pagination": {"page": page, "per_page": per_page, "total": total,
                         "total_pages": total_pages},
        "sort_by": sort_by,
        "filters": filters or {},
        "seo": {"title": f"{category.get('name', '')} Apps | OpenSkill Marketplace",
                "description": category.get("description", "")[:160]},
    }
