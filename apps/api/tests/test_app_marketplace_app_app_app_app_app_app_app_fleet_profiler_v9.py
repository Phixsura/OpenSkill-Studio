from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_profiler_v9 import fleet_profiler_v9
def test_prof_v9():
    r = fleet_profiler_v9([{"status": "completed", "hotspots": 3, "cpu_pct": 45}])
    assert r["hotspots"] == 3
    assert r["healthy"]
