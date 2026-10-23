"""App detail page — complete app detail page aggregator."""

import html


def build_app_detail_page(*, app: dict, reviews: list[dict],
                             related_apps: list[dict]) -> dict:
    safe_name = html.escape(app.get("name", ""))
    rating = app.get("avg_rating", 0)
    installs = app.get("install_count", 0)
    return {
        "header": {
            "name": safe_name,
            "developer": html.escape(app.get("developer", "")),
            "tagline": html.escape(app.get("tagline", "")),
            "rating": round(rating, 1),
            "install_count": installs,
            "price": app.get("price", 0),
            "version": app.get("version", ""),
        },
        "description": html.escape(app.get("description", "")),
        "screenshots": app.get("screenshots", []),
        "reviews": {
            "total": len(reviews),
            "avg_rating": round(sum(r.get("rating", 0) for r in reviews) / max(len(reviews), 1), 1),
            "recent": reviews[:5],
        },
        "related_apps": [{"id": a["id"], "name": a["name"]} for a in related_apps[:6]],
        "permissions": app.get("permissions", []),
        "changelog": app.get("changelog", [])[:5],
        "tabs": ["Overview", "Reviews", "Changelog", "Documentation"],
    }
