from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v140 import platform_v140
def test_v140():
    r = platform_v140()
    assert r["version"] == "140.0"
    assert "140" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
