from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_config_validation_v9 import fleet_config_validation_v9
def test_cv2_v9():
    r = fleet_config_validation_v9([{"valid": True, "schema": "v1"}])
    assert r["invalid"] == 0
    assert r["healthy"]
