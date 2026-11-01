from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_err_budget import fleet_ai_error_budget
def test_eb():
    r = fleet_ai_error_budget([{"active": True, "remaining_pct": 75, "burn_rate": 0.5, "slos": 20}])
    assert r["remaining_pct"] == 75.0
    assert r["safe"]
