from app.services.app_marketplace_app_app_app_app_app_app_app_dev_analytics_ov import build_developer_analytics

def test_analytics():
    r = build_developer_analytics(developer_id="dev1", apps=[
        {"name": "App A", "installs": 50000, "api_calls": 1000000, "revenue": 5000, "rating": 4.8},
        {"name": "App B", "installs": 30000, "api_calls": 500000, "revenue": 2000, "rating": 3.5, "error_rate": 3},
    ])
    assert r["app_count"] == 2
    assert r["total_installs"] == 80000
    assert r["total_revenue"] == 7000
    assert r["top_app"]["name"] == "App A"
    assert len(r["growth_areas"]) == 2
