from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_bench_v2 import fleet_ai_benchmark_v2
def test_bv2():
    r = fleet_ai_benchmark_v2([{"active": True, "models": 200, "tasks": 100, "entries": 500}])
    assert r["models"] == 200
    assert r["competitive"]
