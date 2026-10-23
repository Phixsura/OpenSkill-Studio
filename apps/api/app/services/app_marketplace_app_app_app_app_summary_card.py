"""App summary card — compact app summary for dashboards and lists."""

import html


def build_app_summary(*, app: dict) -> dict:
    rating = app.get("rating", 0)
    installs = app.get("installs", 0)
    return {
        "id": app.get("id", ""),
        "name": html.escape(app.get("name", "")),
        "icon": app.get("icon", "📦"),
        "tagline": html.escape(app.get("tagline", "")),
        "version": app.get("version", "1.0.0"),
        "rating": rating,
        "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
        "installs": installs,
        "installs_display": f"{installs/1000:.1f}K" if installs >= 1000 else str(installs),
        "status": app.get("status", "active"),
        "verified": app.get("verified", False),
        "category": app.get("category", ""),
        "author": html.escape(app.get("author", "")),
    }


def build_app_list(*, apps: list[dict]) -> dict:
    items = [build_app_summary(app=a) for a in apps]
    total_installs = sum(a.get("installs", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": items, "total": len(items),
            "total_installs": total_installs, "avg_rating": avg_rating}
