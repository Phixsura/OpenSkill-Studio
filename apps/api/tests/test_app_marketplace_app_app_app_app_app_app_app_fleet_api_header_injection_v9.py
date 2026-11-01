from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_header_injection_v9 import fleet_api_header_injection_v9
def test_ahi_v9():
    r = fleet_api_header_injection_v9([{"header_injection_protected": True, "blocked_today": 10}])
    assert r["protected"] == 1
    assert r["healthy"]
