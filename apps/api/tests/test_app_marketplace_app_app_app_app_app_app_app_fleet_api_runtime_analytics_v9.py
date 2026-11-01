from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_runtime_analytics_v9 import fleet_api_runtime_analytics_v9
def test_ara2_v9():
    r = fleet_api_runtime_analytics_v9([{"instrumented": True, "cpu_pct": 40, "mem_mb": 256}])
    assert r["instrumented"] == 1
    assert r["healthy"]
