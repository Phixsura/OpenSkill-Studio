from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_load_test import fleet_ai_load_test
def test_lt():
    r = fleet_ai_load_test([{"active": True, "tests_24h": 50, "max_rps": 100000, "p99_ms": 80, "error_pct": 0.1}])
    assert r["max_rps"] == 100000
    assert r["performant"]
