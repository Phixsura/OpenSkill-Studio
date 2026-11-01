from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v220 import platform_v220
def test_v220():
    r = platform_v220()
    assert r["version"] == "220.0"
    assert "NEVER STOPS" in r["status"]
