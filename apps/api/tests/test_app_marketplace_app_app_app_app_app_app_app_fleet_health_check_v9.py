from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_health_check_v9 import fleet_health_check_v9
def test_hc_v9():
    r = fleet_health_check_v9([{"status": "up", "latency_ms": 15}, {"status": "up", "latency_ms": 20}])
    assert r["up"] == 2
    assert r["down"] == 0
    assert r["healthy"]
