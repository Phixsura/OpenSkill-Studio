from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_error_budget_v9 import fleet_api_error_budget_v9
def test_aeb_v9():
    r = fleet_api_error_budget_v9([{"burn_rate": 0.5, "budget_remaining": 90}])
    assert r["burning_fast"] == 0
    assert r["healthy"]
