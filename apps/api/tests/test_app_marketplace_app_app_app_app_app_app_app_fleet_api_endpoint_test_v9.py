from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_endpoint_test_v9 import fleet_api_endpoint_test_v9
def test_aet_v9():
    r = fleet_api_endpoint_test_v9([{"passed": 500, "failed": 0, "skipped": 5}])
    assert r["passed"] == 500
    assert r["healthy"]
