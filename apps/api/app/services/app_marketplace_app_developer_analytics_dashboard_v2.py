"""Developer analytics dashboard v2 — real-time metrics with sparklines and trends."""


def build_analytics_dashboard_v2(*, app: dict, metrics: dict, trends: dict,
                                     top_endpoints: list[dict]) -> dict:
    cards = [
        {"key": "installs", "label": "Installs", "value": metrics.get("installs", 0),
         "trend": trends.get("installs", 0), "icon": "📥"},
        {"key": "api_calls", "label": "API Calls", "value": metrics.get("api_calls", 0),
         "trend": trends.get("api_calls", 0), "icon": "🌐"},
        {"key": "errors", "label": "Errors", "value": metrics.get("errors", 0),
         "trend": trends.get("errors", 0), "icon": "❌"},
        {"key": "response_ms", "label": "Avg Response", "value": f"{metrics.get('avg_response_ms', 0)}ms",
         "trend": trends.get("avg_response_ms", 0), "icon": "⚡"},
    ]
    return {
        "page_type": "analytics_v2",
        "app": {"id": app["id"], "name": app["name"]},
        "cards": cards,
        "top_endpoints": top_endpoints[:5],
        "time_range": metrics.get("time_range", "30d"),
    }


def compute_sparkline(*, data_points: list[int], width: int = 7) -> list[int]:
    if not data_points:
        return [0] * width
    if len(data_points) <= width:
        return data_points + [0] * (width - len(data_points))
    step = len(data_points) / width
    return [data_points[int(i * step)] for i in range(width)]
