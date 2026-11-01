from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v340 import platform_v340
def test_v340():
    r = platform_v340()
    assert r["version"] == "340.0"
    assert "NEVER STOPS" in r["status"]
