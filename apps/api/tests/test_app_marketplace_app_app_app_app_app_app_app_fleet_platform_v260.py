from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v260 import platform_v260
def test_v260():
    r = platform_v260()
    assert r["version"] == "260.0"
    assert "NEVER STOPS" in r["status"]
