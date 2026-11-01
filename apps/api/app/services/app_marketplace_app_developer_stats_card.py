"""Developer stats card — summary stats for developer dashboard."""


def build_stats_card(*, stats: dict) -> dict:
    cards = [
        {"id": "apps", "label": "Published Apps", "value": stats.get("app_count", 0),
         "icon": "📦", "change": stats.get("app_change", 0)},
        {"id": "installs", "label": "Total Installs", "value": stats.get("total_installs", 0),
         "icon": "📥", "change": stats.get("install_change", 0)},
        {"id": "revenue", "label": "Revenue", "value": stats.get("revenue", 0),
         "icon": "💰", "format": "currency", "change": stats.get("revenue_change", 0)},
        {"id": "rating", "label": "Avg Rating", "value": stats.get("avg_rating", 0),
         "icon": "⭐", "change": stats.get("rating_change", 0)},
        {"id": "reviews", "label": "Reviews", "value": stats.get("review_count", 0),
         "icon": "💬", "change": stats.get("review_change", 0)},
        {"id": "api_calls", "label": "API Calls", "value": stats.get("api_calls", 0),
         "icon": "⚡", "change": stats.get("api_change", 0)},
    ]
    return {"cards": cards, "total_cards": len(cards)}
