"""Developer metrics summary — quick metrics overview for the developer dashboard."""


def build_metrics_summary(*, apps: list[dict], period: str = "30d") -> dict:
    total_installs = sum(a.get("install_count", 0) for a in apps)
    total_api = sum(a.get("api_calls", 0) for a in apps)
    ratings = [a.get("avg_rating", 0) for a in apps if a.get("avg_rating", 0) > 0]
    avg_rating = round(sum(ratings) / max(len(ratings), 1), 2)
    total_revenue = sum(a.get("revenue_cents", 0) for a in apps)
    return {
        "period": period,
        "metrics": [
            {"key": "installs", "label": "Installs", "value": total_installs, "icon": "📥",
             "format": "number"},
            {"key": "api_calls", "label": "API Calls", "value": total_api, "icon": "🌐",
             "format": "number"},
            {"key": "rating", "label": "Avg Rating", "value": avg_rating, "icon": "⭐",
             "format": "rating"},
            {"key": "revenue", "label": "Revenue", "value": total_revenue, "icon": "💰",
             "format": "currency"},
            {"key": "apps", "label": "Published", "value": sum(1 for a in apps if a.get("status") == "published"),
             "icon": "📦", "format": "number"},
        ],
    }
