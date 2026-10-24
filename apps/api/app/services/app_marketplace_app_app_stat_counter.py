"""Stat counter — animated counter configurations for dashboards."""


def build_stat_counters(*, metrics: dict) -> dict:
    counters = []
    definitions = {
        "total_apps": {"label": "Total Apps", "icon": "📦", "format": "number"},
        "total_users": {"label": "Total Users", "icon": "👥", "format": "compact"},
        "total_revenue": {"label": "Revenue", "icon": "💰", "format": "currency"},
        "avg_rating": {"label": "Avg Rating", "icon": "⭐", "format": "decimal"},
        "uptime": {"label": "Uptime", "icon": "🟢", "format": "percentage"},
        "api_calls": {"label": "API Calls", "icon": "⚡", "format": "compact"},
    }
    for key, value in metrics.items():
        defn = definitions.get(key, {"label": key.replace("_", " ").title(), "icon": "📊", "format": "number"})
        counters.append({"key": key, "value": value, **defn, "animate": True})
    return {"counters": counters, "total": len(counters)}
