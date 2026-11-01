from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v160 import platform_v160
def test_v160():
    r = platform_v160()
    assert r["version"] == "160.0"
    assert "NEVER STOPS" in r["status"]
