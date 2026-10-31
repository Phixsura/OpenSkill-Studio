from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v280 import platform_v280
def test_v280():
    r = platform_v280()
    assert r["version"] == "280.0"
    assert "NEVER STOPS" in r["status"]
