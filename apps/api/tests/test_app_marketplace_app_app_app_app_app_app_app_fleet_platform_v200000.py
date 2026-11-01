from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v200000 import platform_v200000
def test_v200000():
    r = platform_v200000()
    assert r["version"] == "200000.0"
    assert "TWO HUNDRED THOUSAND" in r["milestone"]
    assert r["lines"] >= 1500000
    assert "NEVER STOPS" in r["status"]
