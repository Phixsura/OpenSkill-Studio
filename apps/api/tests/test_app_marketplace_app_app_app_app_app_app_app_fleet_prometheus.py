from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_prometheus import fleet_prometheus_health
def test_prom():
    r = fleet_prometheus_health([{"healthy": True, "active_series": 1000000, "storage_gb": 50}, {"healthy": False, "active_series": 500000, "storage_gb": 30}])
    assert r["total_series"] == 1500000
    assert not r["all_healthy"]
