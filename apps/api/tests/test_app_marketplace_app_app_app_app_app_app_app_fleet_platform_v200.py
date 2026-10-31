from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_v200 import platform_v200
def test_v200():
    r = platform_v200()
    assert r["version"] == "200.0"
    assert "TWO HUNDRED" in r["milestone"]
    assert r["modules"] == 10
    assert r["dora"]["overall"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
