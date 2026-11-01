from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sdk_adopt import fleet_sdk_adoption
def test_adopt():
    r = fleet_sdk_adoption([{"sdk_version": "2.0", "outdated": False}, {"sdk_version": "1.0", "outdated": True}])
    assert r["outdated"] == 1
    assert r["up_to_date"] == 1
