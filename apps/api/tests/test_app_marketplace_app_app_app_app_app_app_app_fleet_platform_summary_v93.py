from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_summary_v93 import fleet_platform_summary_v93
def test_summary_v93():
    r = fleet_platform_summary_v93()
    assert r["dora"]["overall"] == "ELITE"
    assert len(r["modules"]) == 10
    assert "NEVER STOPS" in r["status"]
