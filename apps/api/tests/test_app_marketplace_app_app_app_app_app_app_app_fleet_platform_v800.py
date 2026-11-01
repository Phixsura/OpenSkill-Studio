from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v800 import platform_v800
def test_v800():
    r = platform_v800()
    assert r["version"] == "800.0"
    assert "EIGHT HUNDRED" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
