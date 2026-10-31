from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_input_san import fleet_ai_input_sanitizer
def test_is():
    r = fleet_ai_input_sanitizer([{"active": True, "sanitized_24h": 50000000, "threats": 1000, "rules": 100}])
    assert r["sanitized_24h"] == 50000000
    assert r["protecting"]
