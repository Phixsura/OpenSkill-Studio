from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_bench_v3 import fleet_ai_platform_benchmark_v3
def test_pbv3():
    r = fleet_ai_platform_benchmark_v3([{"active": True, "tests": 1000, "p99_ms": 50, "throughput_rps": 5000000}])
    assert r["tests"] == 1000
    assert r["performant"]
