"""Similar apps — content-based app recommendation."""

import html


def find_similar_apps(*, app: dict, catalog: list[dict], limit: int = 6) -> dict:
    app_tags = set(app.get("tags", []))
    app_cat = app.get("category", "")
    app_id = app.get("id", "")
    scored = []
    for other in catalog:
        if other.get("id") == app_id:
            continue
        other_tags = set(other.get("tags", []))
        tag_overlap = len(app_tags & other_tags)
        cat_match = 1 if other.get("category") == app_cat else 0
        score = tag_overlap * 2 + cat_match * 3
        if score > 0:
            scored.append({
                "id": other["id"], "name": html.escape(other.get("name", "")),
                "icon": other.get("icon", "📦"), "category": other.get("category", ""),
                "rating": other.get("rating", 0), "score": score,
            })
    scored.sort(key=lambda x: (-x["score"], -x["rating"]))
    return {"similar": scored[:limit], "total_found": len(scored),
            "based_on": {"tags": sorted(app_tags), "category": app_cat}}
