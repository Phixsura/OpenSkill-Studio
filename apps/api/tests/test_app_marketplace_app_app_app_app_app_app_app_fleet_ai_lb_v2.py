from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lb_v2 import fleet_ai_load_balancer_v2
def test_lb():
    r = fleet_ai_load_balancer_v2([{"active": True, "backends": 20, "rps": 500000, "algorithm": "least_connections"}])
    assert r["backends"] == 20
    assert r["distributed"]
