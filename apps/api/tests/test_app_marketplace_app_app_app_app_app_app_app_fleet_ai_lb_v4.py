from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lb_v4 import fleet_ai_load_balancer_v4
def test_lbv4():
    r = fleet_ai_load_balancer_v4([{"active": True, "backends": 100, "rps": 10000000, "hc_s": 5}])
    assert r["backends"] == 100
    assert r["balanced"]
