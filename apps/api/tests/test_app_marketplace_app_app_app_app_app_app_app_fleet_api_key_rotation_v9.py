from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_key_rotation_v9 import fleet_api_key_rotation_v9
def test_akr_v9():
    r = fleet_api_key_rotation_v9([{"rotated_recently": True, "expired": False, "age_days": 15}])
    assert r["expired"] == 0
    assert r["healthy"]
