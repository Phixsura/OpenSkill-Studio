from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v270 import platform_v270
def test_v270():
    r = platform_v270()
    assert r["version"] == "270.0"
    assert "NEVER STOPS" in r["status"]
