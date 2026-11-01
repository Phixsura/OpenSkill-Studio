from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_request_transform_v9 import fleet_api_request_transform_v9
def test_arx_v9():
    r = fleet_api_request_transform_v9([{"active": True, "applied_today": 50000, "errors": 0}])
    assert r["applied_today"] == 50000
    assert r["healthy"]
