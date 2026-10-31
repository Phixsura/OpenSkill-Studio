from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_perf_profile_v9 import fleet_perf_profile_v9
def test_pp_v9():
    r = fleet_perf_profile_v9([{"type": "cpu", "hotspots_found": 3}, {"type": "memory", "hotspots_found": 1}])
    assert r["cpu"] == 1
    assert r["hotspots_found"] == 4
    assert r["healthy"]
