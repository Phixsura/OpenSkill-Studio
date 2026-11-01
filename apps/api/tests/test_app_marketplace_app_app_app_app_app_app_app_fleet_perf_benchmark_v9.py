from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_perf_benchmark_v9 import fleet_perf_benchmark_v9
def test_pb_v9():
    r = fleet_perf_benchmark_v9([{"passed": True, "regressed": False, "p99_ms": 50}])
    assert r["passed"] == 1
    assert r["regressed"] == 0
    assert r["healthy"]
