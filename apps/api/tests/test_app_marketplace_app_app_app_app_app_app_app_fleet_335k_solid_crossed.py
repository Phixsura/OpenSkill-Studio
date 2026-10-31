from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_335k_solid_crossed import fleet_335k_solid
def test_335k_solid():
    r = fleet_335k_solid()
    assert "335,000" in r["milestone"]
