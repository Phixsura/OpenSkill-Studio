"""App gallery — grid/list view modes for browsing marketplace apps."""

from collections import defaultdict


def build_gallery(*, apps: list[dict], view_mode: str = "grid", sort_by: str = "popular",
                     page: int = 1, per_page: int = 24) -> dict:
    # Sort
    if sort_by == "popular":
        apps = sorted(apps, key=lambda a: -a.get("install_count", 0))
    elif sort_by == "rating":
        apps = sorted(apps, key=lambda a: -a.get("avg_rating", 0))
    elif sort_by == "newest":
        apps = sorted(apps, key=lambda a: a.get("created_at", ""), reverse=True)
    elif sort_by == "name":
        apps = sorted(apps, key=lambda a: a.get("name", "").lower())
    total = len(apps)
    start = (page - 1) * per_page
    page_apps = apps[start:start + per_page]
    return {"apps": page_apps, "view_mode": view_mode, "sort_by": sort_by,
            "page": page, "per_page": per_page, "total": total,
            "total_pages": max(1, (total + per_page - 1) // per_page),
            "columns": 4 if view_mode == "grid" else 1}


def get_sort_options() -> list[dict]:
    return [
        {"id": "popular", "label": "Most Popular", "icon": "🔥"},
        {"id": "rating", "label": "Highest Rated", "icon": "⭐"},
        {"id": "newest", "label": "Newest First", "icon": "🆕"},
        {"id": "name", "label": "Alphabetical", "icon": "🔤"},
    ]


def get_view_modes() -> list[dict]:
    return [{"id": "grid", "label": "Grid", "icon": "▦"}, {"id": "list", "label": "List", "icon": "☰"}]
