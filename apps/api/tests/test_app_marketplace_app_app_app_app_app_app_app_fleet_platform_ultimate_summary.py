from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_ultimate_summary import fleet_ultimate_summary
def test_ultimate():
    r = fleet_ultimate_summary()
    assert r["dora"] == "ELITE"
    assert r["modules"] == 10
    assert "NEVER STOPS" in r["status"]
