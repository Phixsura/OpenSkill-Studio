from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v190 import platform_v190
def test_v190():
    r = platform_v190()
    assert r["version"] == "190.0"
    assert "v200" in r["status"]
    assert "NEVER STOPS" in r["status"]
