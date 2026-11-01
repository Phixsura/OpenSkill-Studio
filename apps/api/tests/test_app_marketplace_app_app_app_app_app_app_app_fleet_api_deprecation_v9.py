from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_deprecation_v9 import fleet_api_deprecation_v9
def test_ad2_v9():
    r = fleet_api_deprecation_v9([{"deprecated": True, "migrated": True, "remaining_consumers": 0}])
    assert r["migrated"] == 1
    assert r["healthy"]
