from app.services.app_marketplace_app_final_platform_aggregator import build_final_platform_view

def test_final():
    v = build_final_platform_view(
        marketplace={"apps": 500, "categories": 8},
        developer={"sdks": ["ts", "py"], "docs": True},
        infrastructure={"regions": 4, "uptime": 99.99},
        community={"members": 1000, "discussions": 500})
    assert v["page_type"] == "complete_platform"
    assert v["platform_version"] == "1.0.0"
    assert v["feature_count"] > 0
