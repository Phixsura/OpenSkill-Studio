from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_request_priority_v9 import fleet_api_request_priority_v9
def test_arp2_v9():
    r = fleet_api_request_priority_v9([{"priority": "high", "requests_today": 50000}])
    assert r["high"] == 1
    assert r["healthy"]
