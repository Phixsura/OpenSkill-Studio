from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_cors_v9 import fleet_api_cors_v9
def test_acors_v9():
    r = fleet_api_cors_v9([{"cors_configured": True, "allow_origin": "https://app.example.com", "preflight_requests": 500}])
    assert r["wildcard_origins"] == 0
    assert r["healthy"]
