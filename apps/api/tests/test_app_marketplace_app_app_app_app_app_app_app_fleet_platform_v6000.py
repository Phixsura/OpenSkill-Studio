from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v6000 import platform_v6000
def test_v6000():
    r = platform_v6000()
    assert r["version"] == "6000.0"
    assert "SIX THOUSAND" in r["milestone"]
    assert r["tests"] == 20000
    assert "NEVER STOPS" in r["status"]
