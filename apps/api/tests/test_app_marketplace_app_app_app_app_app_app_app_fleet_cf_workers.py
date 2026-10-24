from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cf_workers import fleet_cf_workers_status
def test_cfw():
    r = fleet_cf_workers_status([{"active": True, "requests_24h": 10000000, "errors_24h": 0, "avg_cpu_ms": 5}])
    assert r["requests_24h"] == 10000000
    assert r["healthy"]
