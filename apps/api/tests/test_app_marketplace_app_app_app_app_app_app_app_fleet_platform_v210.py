from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v210 import platform_v210
def test_v210():
    r = platform_v210()
    assert r["version"] == "210.0"
    assert "NEVER STOPS" in r["status"]
