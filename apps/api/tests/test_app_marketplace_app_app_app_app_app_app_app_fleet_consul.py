from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_consul import fleet_consul_status
def test_consul():
    r = fleet_consul_status([{"healthy": True, "services": 100, "kv_keys": 5000}, {"healthy": True, "services": 80, "kv_keys": 3000}])
    assert r["services"] == 180
    assert r["kv_keys"] == 8000
    assert r["all_healthy"]
