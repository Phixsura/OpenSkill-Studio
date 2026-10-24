from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_client_sdk_v9 import fleet_api_client_sdk_v9
def test_acs2_v9():
    r = fleet_api_client_sdk_v9([{"up_to_date": True, "weekly_downloads": 50000, "open_issues": 0}])
    assert r["weekly_downloads"] == 50000
    assert r["healthy"]
