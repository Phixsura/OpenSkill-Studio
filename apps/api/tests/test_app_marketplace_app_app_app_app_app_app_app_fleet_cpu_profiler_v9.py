from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cpu_profiler_v9 import fleet_cpu_profiler_v9
def test_cpup_v9():
    r = fleet_cpu_profiler_v9([{"collected": True, "hotspots": 3, "cpu_pct": 45}])
    assert r["hotspots"] == 3
    assert r["healthy"]
