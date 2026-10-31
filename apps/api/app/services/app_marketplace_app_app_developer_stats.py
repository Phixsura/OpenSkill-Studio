"""Developer stats — comprehensive developer account statistics."""

import html


def build_developer_stats(*, developer: dict, apps: list[dict]) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_reviews = sum(a.get("review_count", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1) if apps else 0
    top_app = max(apps, key=lambda a: a.get("installs", 0)) if apps else None
    return {
        "developer": html.escape(developer.get("name", "")),
        "member_since": developer.get("member_since", ""),
        "summary": {
            "total_apps": len(apps),
            "total_installs": total_installs,
            "installs_display": f"{total_installs:,}",
            "total_reviews": total_reviews,
            "avg_rating": avg_rating,
            "top_app": html.escape(top_app.get("name", "")) if top_app else None,
        },
        "badges": _earn_badges(total_installs=total_installs, app_count=len(apps), avg_rating=avg_rating),
    }


def _earn_badges(*, total_installs: int, app_count: int, avg_rating: float) -> list[dict]:
    badges = []
    if total_installs >= 100000:
        badges.append({"id": "100k_installs", "label": "100K Club", "icon": "🏆"})
    if app_count >= 10:
        badges.append({"id": "prolific", "label": "Prolific Developer", "icon": "⚡"})
    if avg_rating >= 4.5:
        badges.append({"id": "top_quality", "label": "Top Quality", "icon": "⭐"})
    if app_count >= 1:
        badges.append({"id": "first_app", "label": "App Creator", "icon": "🎯"})
    return badges
