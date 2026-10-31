from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v130 import platform_v130
def test_v130():
    r = platform_v130()
    assert r["version"] == "130.0"
    assert "130" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
