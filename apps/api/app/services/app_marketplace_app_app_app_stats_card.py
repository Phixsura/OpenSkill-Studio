"""App stats card — compact app statistics display."""

import html


def _compact(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)


def build_app_stats_card(*, app: dict) -> dict:
    installs = app.get("installs", 0)
    active = app.get("active_users", 0)
    rating = app.get("rating", 0)
    retention = round(active / max(installs, 1) * 100, 1) if installs else 0
    return {
        "name": html.escape(app.get("name", "")),
        "icon": app.get("icon", "📦"),
        "metrics": [
            {"label": "Installs", "value": installs, "display": _compact(installs), "icon": "📥"},
            {"label": "Active", "value": active, "display": _compact(active), "icon": "👥"},
            {"label": "Rating", "value": rating, "display": f"{rating:.1f}", "icon": "⭐"},
            {"label": "Retention", "value": retention, "display": f"{retention}%", "icon": "🔄"},
        ],
        "health": "good" if rating >= 4 and retention >= 50 else "ok" if rating >= 3 else "poor",
    }
