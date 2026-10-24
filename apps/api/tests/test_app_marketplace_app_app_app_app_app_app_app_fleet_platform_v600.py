from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v600 import platform_v600
def test_v600():
    r = platform_v600()
    assert r["version"] == "600.0"
    assert "SIX HUNDRED" in r["milestone"]
    assert r["dora"]["overall"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
