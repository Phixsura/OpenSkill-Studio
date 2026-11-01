from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_consist import fleet_api_consistency
def test_consist():
    r = fleet_api_consistency([{"follows_convention": True}, {"follows_convention": True}, {"follows_convention": False}])
    assert r["score"] == 66.7
    assert r["inconsistent"] == 1
