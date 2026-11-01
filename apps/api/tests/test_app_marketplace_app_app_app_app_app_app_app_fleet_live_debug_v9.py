from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_live_debug_v9 import fleet_live_debug_v9
def test_ld_v9():
    r = fleet_live_debug_v9([{"active": True, "breakpoints": 5, "duration_min": 15}])
    assert r["active"] == 1
    assert r["healthy"]
