from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_request_dedup_v9 import fleet_api_request_dedup_v9
def test_ard_v9():
    r = fleet_api_request_dedup_v9([{"dedup_enabled": True, "duplicates_caught": 100, "total_requests": 100000}])
    assert r["duplicates_caught"] == 100
    assert r["healthy"]
