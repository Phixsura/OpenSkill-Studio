from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_grad_mon import fleet_ai_gradient_monitor
def test_gm():
    r = fleet_ai_gradient_monitor([{"active": True, "jobs": 50, "vanishing": 0, "exploding": 0, "healthy": 50}])
    assert r["healthy"] == 50
    assert r["stable"]
