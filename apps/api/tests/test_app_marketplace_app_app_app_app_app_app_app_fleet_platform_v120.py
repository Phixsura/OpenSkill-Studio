from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v120 import platform_v120
def test_v120():
    r = platform_v120()
    assert r["version"] == "120.0"
    assert "120" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
