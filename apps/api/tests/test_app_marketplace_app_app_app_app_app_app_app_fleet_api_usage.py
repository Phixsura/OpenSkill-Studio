from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_usage import fleet_api_usage
def test_usage():
    r = fleet_api_usage([{"name": "/health", "calls_24h": 50000}, {"name": "/old", "calls_24h": 0}])
    assert r["total_calls"] == 50000
    assert r["unused"] == 1
    assert r["top_endpoint"] == "/health"
