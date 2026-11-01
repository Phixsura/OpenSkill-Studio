from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scale_dec import fleet_scaling_decision
def test_scale_up():
    assert fleet_scaling_decision(85, 60, 500)["action"] == "scale_up"
def test_scale_down():
    assert fleet_scaling_decision(20, 30, 5)["action"] == "scale_down"
def test_steady():
    assert fleet_scaling_decision(50, 50, 100)["action"] == "steady"
