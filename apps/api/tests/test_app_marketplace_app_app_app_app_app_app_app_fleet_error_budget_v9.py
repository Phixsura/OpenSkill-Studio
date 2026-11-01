from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_error_budget_v9 import fleet_error_budget_v9
def test_eb_v9():
    r = fleet_error_budget_v9([{"burn_rate": 0.5, "budget_pct": 90, "alerts": 0}])
    assert r["burning_fast"] == 0
    assert r["healthy"]
