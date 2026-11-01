from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_global_lb_v9 import fleet_global_lb_v9
def test_glb_v9():
    r = fleet_global_lb_v9([{"active": True, "rps": 50000, "failovers_today": 0}])
    assert r["total_rps"] == 50000
    assert r["healthy"]
