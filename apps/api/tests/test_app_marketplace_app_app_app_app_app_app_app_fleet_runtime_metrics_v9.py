from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_runtime_metrics_v9 import fleet_runtime_metrics_v9
def test_rm_v9():
    r = fleet_runtime_metrics_v9([{"memory_gb": 16, "cpu_cores": 4, "gc_pause_ms": 5}])
    assert r["total_memory_gb"] == 16.0
    assert r["healthy"]
