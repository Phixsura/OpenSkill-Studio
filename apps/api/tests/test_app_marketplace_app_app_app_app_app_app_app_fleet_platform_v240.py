from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v240 import platform_v240
def test_v240():
    r = platform_v240()
    assert r["version"] == "240.0"
    assert "NEVER STOPS" in r["status"]
