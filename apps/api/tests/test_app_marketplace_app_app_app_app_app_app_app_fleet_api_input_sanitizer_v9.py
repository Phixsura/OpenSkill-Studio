from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_input_sanitizer_v9 import fleet_api_input_sanitizer_v9
def test_ais_v9():
    r = fleet_api_input_sanitizer_v9([{"sanitization_enabled": True, "xss_blocked": 50, "sqli_blocked": 10}])
    assert r["sanitized"] == 1
    assert r["healthy"]
