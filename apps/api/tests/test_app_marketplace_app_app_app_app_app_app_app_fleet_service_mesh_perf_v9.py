from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_mesh_perf_v9 import fleet_service_mesh_perf_v9
def test_smp_v9():
    r = fleet_service_mesh_perf_v9([{"overhead_ms": 1.5, "cpu_overhead_pct": 2, "mem_overhead_mb": 50}])
    assert r["avg_overhead_ms"] == 1.5
    assert r["healthy"]
