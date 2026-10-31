"""Complete marketplace stats — comprehensive statistics for the entire platform."""


def build_complete_marketplace_stats(*, apps: list[dict], developers: list[dict],
                                         installs: list[dict], reviews: list[dict],
                                         api_calls_today: int) -> dict:
    published = sum(1 for a in apps if a.get("status") == "published")
    verified = sum(1 for d in developers if d.get("verified"))
    active_installs = sum(1 for i in installs if i.get("status") == "active")
    avg_rating = round(sum(r.get("rating", 0) for r in reviews) / max(len(reviews), 1), 2)
    categories = len(set(a.get("category") for a in apps if a.get("category")))
    return {
        "headline": [
            {"label": "Apps", "value": len(apps), "published": published, "icon": "📦"},
            {"label": "Developers", "value": len(developers), "verified": verified, "icon": "👨‍💻"},
            {"label": "Installations", "value": len(installs), "active": active_installs, "icon": "📥"},
            {"label": "Reviews", "value": len(reviews), "avg_rating": avg_rating, "icon": "⭐"},
            {"label": "API Calls Today", "value": api_calls_today, "icon": "🌐"},
        ],
        "meta": {"categories": categories, "total_apps": len(apps), "total_developers": len(developers)},
    }
