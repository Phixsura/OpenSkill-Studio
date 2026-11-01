from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_load_balancer_v9 import fleet_load_balancer_v9
def test_lb_v9():
    r = fleet_load_balancer_v9([{"healthy_backends": 4, "total_backends": 4, "active_connections": 1000}])
    assert r["healthy_backends"] == 4
    assert r["active_connections"] == 1000
    assert r["healthy"]
