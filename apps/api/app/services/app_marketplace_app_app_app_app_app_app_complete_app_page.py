"""Complete app page — the ultimate app detail page with everything."""

import html


def build_complete_app_page(*, app: dict, developer: dict, stats: dict,
                               reviews: list[dict], similar: list[dict],
                               changelog: list[dict], installed: bool = False) -> dict:
    rating = stats.get("avg_rating", 0)
    review_count = len(reviews)
    return {
        "app": {
            "id": app.get("id", ""), "name": html.escape(app.get("name", "")),
            "icon": app.get("icon", "📦"), "tagline": html.escape(app.get("tagline", "")),
            "description": html.escape(app.get("description", "")),
            "version": app.get("version", "1.0.0"), "pricing": app.get("pricing", "Free"),
            "tags": app.get("tags", []), "screenshots": app.get("screenshots", []),
        },
        "developer": {
            "name": html.escape(developer.get("name", "")),
            "verified": developer.get("verified", False),
            "app_count": developer.get("app_count", 0),
        },
        "stats": {
            "installs": stats.get("installs", 0), "rating": rating,
            "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
            "review_count": review_count, "api_calls": stats.get("api_calls", 0),
        },
        "top_reviews": [{"rating": r.get("rating", 0), "title": html.escape(r.get("title", "")),
                          "author": html.escape(r.get("author", ""))} for r in reviews[:3]],
        "similar_apps": [{"id": s.get("id"), "name": html.escape(s.get("name", "")),
                           "icon": s.get("icon", "📦")} for s in similar[:4]],
        "recent_changelog": [{"version": c.get("version", ""), "title": html.escape(c.get("title", ""))}
                              for c in changelog[:3]],
        "installed": installed,
        "cta": "Open" if installed else "Install" if app.get("pricing") == "Free" else f"Subscribe — {app.get('pricing', '')}",
        "sections": ["overview", "screenshots", "reviews", "changelog", "similar"],
    }
