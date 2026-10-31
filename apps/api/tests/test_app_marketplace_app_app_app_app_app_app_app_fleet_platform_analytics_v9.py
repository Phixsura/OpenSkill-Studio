from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_analytics_v9 import fleet_platform_analytics_v9
def test_pa_v9():
    r = fleet_platform_analytics_v9([{"dau": 10000, "api_calls": 1000000, "avg_latency_ms": 25}])
    assert r["dau"] == 10000
    assert r["healthy"]
