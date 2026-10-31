from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_transform_v9 import fleet_api_transform_v9
def test_at_v9():
    r = fleet_api_transform_v9([{"active": True, "type": "request"}, {"active": True, "type": "response"}])
    assert r["request"] == 1
    assert r["response"] == 1
    assert r["healthy"]
