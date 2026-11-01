"""Complete analytics page — master aggregator for developer analytics."""


def build_complete_analytics_page(*, app: dict, installs_data: dict, api_usage: dict,
                                     error_data: dict, revenue_data: dict | None = None) -> dict:
    return {
        "page_type": "analytics_dashboard",
        "app": {"id": app["id"], "name": app["name"]},
        "panels": [
            {"key": "installs", "title": "Installations", "icon": "📥", "data": installs_data},
            {"key": "api", "title": "API Usage", "icon": "📊", "data": api_usage},
            {"key": "errors", "title": "Errors", "icon": "❌", "data": error_data},
        ] + ([{"key": "revenue", "title": "Revenue", "icon": "💰", "data": revenue_data}] if revenue_data else []),
        "export_formats": ["csv", "json"],
    }
