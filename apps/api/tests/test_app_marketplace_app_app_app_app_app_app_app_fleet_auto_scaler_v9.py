from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_auto_scaler_v9 import fleet_auto_scaler_v9
def test_as_v9():
    r = fleet_auto_scaler_v9([{"action": "stable", "replicas": 5}, {"action": "scale_up", "replicas": 3}])
    assert r["total_replicas"] == 8
    assert r["healthy"]
