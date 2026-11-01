from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lb_health import fleet_lb_health
def test_lb():
    r = fleet_lb_health([{"healthy_backends": 9, "total_backends": 10}, {"healthy_backends": 10, "total_backends": 10}])
    assert r["healthy_backends"] == 19
    assert r["health_pct"] == 95.0
    assert r["ok"]
