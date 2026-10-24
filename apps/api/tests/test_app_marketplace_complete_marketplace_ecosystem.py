from app.services.app_marketplace_complete_marketplace_ecosystem import build_complete_marketplace_ecosystem

def test_ecosystem():
    e = build_complete_marketplace_ecosystem(
        platform={"total_apps": 500, "total_developers": 100, "total_installs": 25000, "total_api_calls": 1000000},
        marketplace={"categories": 8, "collections": 12, "trending": 20},
        developer_tools={"sdk_downloads": 5000, "api_docs_views": 50000, "sandbox_sessions": 300},
        infrastructure={"uptime_pct": 99.99, "avg_response_ms": 120, "active_webhooks": 1500})
    assert e["page_type"] == "ecosystem_overview"
    assert e["platform"]["total_apps"] == 500
    assert e["infrastructure"]["uptime_pct"] == 99.99
    assert len(e["links"]) == 5
