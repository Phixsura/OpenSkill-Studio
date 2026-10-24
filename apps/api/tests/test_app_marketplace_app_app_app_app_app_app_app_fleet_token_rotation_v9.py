from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_token_rotation_v9 import fleet_token_rotation_v9
def test_tr2_v9():
    r = fleet_token_rotation_v9([{"rotated": True, "expired": False, "age_days": 15}])
    assert r["rotated"] == 1
    assert r["healthy"]
