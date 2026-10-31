"""App metric summary — comprehensive app health metrics."""

import html


def build_metric_summary(*, app: dict, period: str = "30d") -> dict:
    installs = app.get("installs", 0)
    active = app.get("active_users", 0)
    api_calls = app.get("api_calls", 0)
    errors = app.get("error_count", 0)
    rating = app.get("avg_rating", 0)
    error_rate = round(errors / max(api_calls, 1) * 100, 2) if api_calls else 0
    engagement = round(active / max(installs, 1) * 100, 1) if installs else 0
    health_score = round((min(rating / 5, 1) * 40) + (min(1 - error_rate / 10, 1) * 30) + (min(engagement / 100, 1) * 30))
    return {
        "app_name": html.escape(app.get("name", "")),
        "period": period,
        "kpis": [
            {"label": "Installs", "value": installs, "display": f"{installs:,}", "icon": "📥"},
            {"label": "Active Users", "value": active, "display": f"{active:,}", "icon": "👥"},
            {"label": "API Calls", "value": api_calls, "display": f"{api_calls:,}", "icon": "🔗"},
            {"label": "Error Rate", "value": error_rate, "display": f"{error_rate}%", "icon": "❌"},
            {"label": "Rating", "value": rating, "display": f"{rating}/5", "icon": "⭐"},
            {"label": "Engagement", "value": engagement, "display": f"{engagement}%", "icon": "📊"},
        ],
        "health_score": health_score,
        "health_grade": "A" if health_score >= 90 else "B" if health_score >= 75 else "C" if health_score >= 60 else "F",
    }
