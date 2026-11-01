from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v125_335k import platform_v125_335k
def test_v125():
    r = platform_v125_335k()
    assert r["version"] == "125.0"
    assert "335,000" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
