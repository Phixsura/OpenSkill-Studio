from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tech_debt import fleet_tech_debt
def test_debt():
    r = fleet_tech_debt([{"debt_hours": 30}, {"debt_hours": 150}, {"debt_hours": 20}])
    assert r["total_debt_hours"] == 200
    assert r["high_debt_services"] == 1
    assert not r["manageable"]
