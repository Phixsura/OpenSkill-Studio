"""App detail — complete app detail page data aggregator."""

import html


def build_app_detail(*, app: dict, reviews: list[dict] | None = None,
                       similar: list[dict] | None = None,
                       installed: bool = False) -> dict:
    rating = app.get("rating", 0)
    review_list = reviews or []
    avg_rating = round(sum(r.get("rating", 0) for r in review_list) / max(len(review_list), 1), 1) if review_list else rating
    return {
        "header": {
            "name": html.escape(app.get("name", "")),
            "icon": app.get("icon", "📦"),
            "version": app.get("version", "1.0.0"),
            "author": html.escape(app.get("author", "")),
            "verified": app.get("verified", False),
            "tagline": html.escape(app.get("tagline", "")),
        },
        "description": html.escape(app.get("description", "")),
        "stats": {
            "installs": app.get("installs", 0),
            "rating": avg_rating,
            "stars": "★" * round(avg_rating) + "☆" * (5 - round(avg_rating)),
            "review_count": len(review_list),
        },
        "pricing": app.get("pricing", "Free"),
        "installed": installed,
        "cta": "Open" if installed else ("Install" if app.get("pricing") == "Free" else f"Subscribe — {app.get('pricing', '')}"),
        "screenshots": app.get("screenshots", []),
        "tags": app.get("tags", []),
        "similar_apps": [{"id": s.get("id"), "name": html.escape(s.get("name", "")),
                           "icon": s.get("icon", "📦")} for s in (similar or [])[:4]],
        "has_similar": bool(similar),
    }
