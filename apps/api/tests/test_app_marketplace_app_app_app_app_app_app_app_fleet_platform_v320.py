from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v320 import platform_v320
def test_v320():
    r = platform_v320()
    assert r["version"] == "320.0"
    assert "NEVER STOPS" in r["status"]
