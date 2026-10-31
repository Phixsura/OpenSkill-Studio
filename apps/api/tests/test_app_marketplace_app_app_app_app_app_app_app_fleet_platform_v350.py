from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v350 import platform_v350
def test_v350():
    r = platform_v350()
    assert r["version"] == "350.0"
    assert "350" in r["milestone"]
    assert r["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
