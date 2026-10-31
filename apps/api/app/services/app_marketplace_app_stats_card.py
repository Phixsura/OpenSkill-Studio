"""App stats card builder — build data for the app detail page stats card."""

def build_app_stats_card(*, installs: int, executions: int, webhooks: int, health: int, rating: float, reviews: int) -> dict:
    return {
        "metrics": [
            {"label": "Installs", "value": installs, "icon": "📥"},
            {"label": "Executions", "value": executions, "icon": "⚡"},
            {"label": "Webhooks", "value": webhooks, "icon": "🔔"},
            {"label": "Health", "value": f"{health}%", "icon": "💚" if health >= 90 else "⚠️"},
            {"label": "Rating", "value": f"{rating}/5", "icon": "⭐"},
            {"label": "Reviews", "value": reviews, "icon": "💬"},
        ],
    }
