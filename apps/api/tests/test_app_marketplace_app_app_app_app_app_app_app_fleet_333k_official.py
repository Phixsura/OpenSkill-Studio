from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_333k_official import fleet_333k_official
def test_333k_official():
    r = fleet_333k_official()
    assert "333,000" in r["milestone"]
