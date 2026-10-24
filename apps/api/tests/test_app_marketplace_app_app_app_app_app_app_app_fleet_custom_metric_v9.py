from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_custom_metric_v9 import fleet_custom_metric_v9
def test_cm2_v9():
    r = fleet_custom_metric_v9([{"active": True, "has_alert": True, "data_points_per_min": 1000}])
    assert r["active"] == 1
    assert r["healthy"]
