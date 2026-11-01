from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_grand_summary import fleet_grand_summary
def test_grand():
    r = fleet_grand_summary()
    assert r["dora"]["overall"] == "ELITE"
    assert r["modules"] == 10
    assert "NEVER STOPS" in r["status"]
