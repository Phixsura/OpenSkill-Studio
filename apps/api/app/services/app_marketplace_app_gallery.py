"""Marketplace app gallery — build gallery views for different contexts."""


def build_category_gallery(*, category: str, apps: list[dict], sort_by: str = "installs") -> dict:
    sort_keys = {"installs": "install_count", "newest": "created_at", "rating": "rating", "name": "name"}
    key = sort_keys.get(sort_by, "install_count")
    reverse = sort_by != "name"
    sorted_apps = sorted(apps, key=lambda a: a.get(key, 0), reverse=reverse)
    return {"category": category, "apps": sorted_apps, "total": len(apps), "sort_by": sort_by}


def build_developer_gallery(*, developer_name: str, apps: list[dict]) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    return {"developer": developer_name, "apps": published, "total": len(published),
            "categories": sorted(set(a.get("category", "") for a in published))}
