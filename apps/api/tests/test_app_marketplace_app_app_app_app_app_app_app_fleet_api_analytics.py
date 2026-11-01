from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_analytics import fleet_api_analytics
def test_analytics():
    r = fleet_api_analytics({"total_calls": 100000, "unique_consumers": 500, "top_endpoint": "/api/v1/users"})
    assert r["avg_calls_per_consumer"] == 200.0
    assert r["top_endpoint"] == "/api/v1/users"
