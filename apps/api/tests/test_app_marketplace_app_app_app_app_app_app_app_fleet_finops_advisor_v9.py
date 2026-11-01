from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_finops_advisor_v9 import fleet_finops_advisor_v9
def test_fo_v9():
    r = fleet_finops_advisor_v9([{"implemented": True, "monthly_savings": 1000, "category": "rightsizing"}])
    assert r["potential_savings"] == 1000
    assert r["healthy"]
