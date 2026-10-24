from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eb_remain import fleet_error_budget_remaining
def test_eb():
    r = fleet_error_budget_remaining({"budget_minutes": 43.2, "consumed_minutes": 10})
    assert r["remaining_min"] == 33.2
    assert r["status"] == "safe"
