from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_load_test_v9 import fleet_load_test_v9
def test_lt_v9():
    r = fleet_load_test_v9([{"passed": True, "peak_rps": 50000, "p99_ms": 100}])
    assert r["max_rps"] == 50000
    assert r["healthy"]
