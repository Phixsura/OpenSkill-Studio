from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v400 import platform_v400
def test_v400():
    r = platform_v400()
    assert r["version"] == "400.0"
    assert "FOUR HUNDRED" in r["milestone"]
    assert r["dora"]["overall"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
