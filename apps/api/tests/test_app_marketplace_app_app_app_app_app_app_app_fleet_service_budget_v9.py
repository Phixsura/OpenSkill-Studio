from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_budget_v9 import fleet_service_budget_v9
def test_sb2_v9():
    r = fleet_service_budget_v9([{"spend": 3000, "budget": 5000}])
    assert r["over_budget"] == 0
    assert r["healthy"]
