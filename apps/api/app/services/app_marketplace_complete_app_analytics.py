"""Complete app analytics page — all analytics views combined into one page."""


def build_complete_app_analytics(*, app: dict, installs: dict, api_usage: dict,
                                     reviews: dict, retention: dict, revenue: dict | None,
                                     geo: dict, funnel: dict) -> dict:
    return {
        "page_type": "complete_app_analytics",
        "app": {"id": app["id"], "name": app["name"]},
        "panels": [
            {"key": "installs", "title": "Installations", "icon": "📥", "data": installs},
            {"key": "api", "title": "API Usage", "icon": "🌐", "data": api_usage},
            {"key": "reviews", "title": "Reviews", "icon": "⭐", "data": reviews},
            {"key": "retention", "title": "Retention", "icon": "📊", "data": retention},
            {"key": "geo", "title": "Geography", "icon": "🌍", "data": geo},
            {"key": "funnel", "title": "Conversion Funnel", "icon": "📈", "data": funnel},
        ] + ([{"key": "revenue", "title": "Revenue", "icon": "💰", "data": revenue}] if revenue else []),
        "time_ranges": ["7d", "30d", "90d", "12m", "all"],
        "export_formats": ["csv", "json", "pdf"],
    }
