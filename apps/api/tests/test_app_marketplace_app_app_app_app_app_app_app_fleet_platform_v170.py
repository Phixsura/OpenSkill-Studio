from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v170 import platform_v170
def test_v170():
    r = platform_v170()
    assert r["version"] == "170.0"
    assert "NEVER STOPS" in r["status"]
