from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v330 import platform_v330
def test_v330():
    r = platform_v330()
    assert r["version"] == "330.0"
    assert "ONE-THIRD" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
