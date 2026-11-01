from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scale_hist import fleet_scaling_history
def test_hist():
    r = fleet_scaling_history([{"direction": "up"}, {"direction": "up"}, {"direction": "down"}])
    assert r["scale_ups"] == 2
    assert r["ratio"] == 2.0
