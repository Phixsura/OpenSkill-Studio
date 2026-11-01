from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_330k_official import fleet_330k_official
def test_330k_official():
    r = fleet_330k_official()
    assert "330,000" in r["milestone"]
    assert "NEVER STOPS" in r["status"]
