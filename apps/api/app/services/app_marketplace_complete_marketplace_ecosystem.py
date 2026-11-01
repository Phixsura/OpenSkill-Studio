"""Complete marketplace ecosystem — THE ABSOLUTE FINAL master aggregator of the entire developer platform ecosystem."""


def build_complete_marketplace_ecosystem(*, platform: dict, marketplace: dict,
                                            developer_tools: dict, infrastructure: dict) -> dict:
    return {
        "page_type": "ecosystem_overview",
        "platform": {
            "total_apps": platform.get("total_apps", 0),
            "total_developers": platform.get("total_developers", 0),
            "total_installs": platform.get("total_installs", 0),
            "total_api_calls": platform.get("total_api_calls", 0),
        },
        "marketplace": {
            "categories": marketplace.get("categories", 0),
            "collections": marketplace.get("collections", 0),
            "trending_count": marketplace.get("trending", 0),
        },
        "developer_tools": {
            "sdk_downloads": developer_tools.get("sdk_downloads", 0),
            "api_docs_views": developer_tools.get("api_docs_views", 0),
            "sandbox_sessions": developer_tools.get("sandbox_sessions", 0),
        },
        "infrastructure": {
            "uptime_pct": infrastructure.get("uptime_pct", 99.99),
            "avg_response_ms": infrastructure.get("avg_response_ms", 0),
            "active_webhooks": infrastructure.get("active_webhooks", 0),
        },
        "links": {
            "marketplace": "/marketplace",
            "developer_portal": "/developer",
            "api_docs": "/docs/api",
            "status_page": "/status",
            "community": "/community",
        },
    }
