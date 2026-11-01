from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v180 import platform_v180
def test_v180():
    r = platform_v180()
    assert r["version"] == "180.0"
    assert "NEVER STOPS" in r["status"]
