from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_grand_total import fleet_grand_total
def test_grand():
    r = fleet_grand_total()
    assert r["modules"] == 10
    assert r["status"] == "FULLY OPERATIONAL"
