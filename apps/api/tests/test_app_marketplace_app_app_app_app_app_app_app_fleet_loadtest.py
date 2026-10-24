from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_loadtest import fleet_loadtest_results
def test_load():
    r = fleet_loadtest_results([{"passed": True, "peak_rps": 5000, "p99_ms": 200}, {"passed": False, "peak_rps": 3000, "p99_ms": 800}])
    assert r["passed"] == 1
    assert r["max_rps"] == 5000
    assert not r["all_passed"]
