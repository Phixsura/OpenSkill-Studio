from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v250 import platform_v250
def test_v250():
    r = platform_v250()
    assert r["version"] == "250.0"
    assert "QUARTER THOUSAND" in r["milestone"]
    assert r["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
