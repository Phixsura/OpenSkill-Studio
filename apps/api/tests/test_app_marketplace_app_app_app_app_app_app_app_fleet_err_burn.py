from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_err_burn import fleet_err_budget_burn
def test_burn():
    r = fleet_err_budget_burn([{"burn_rate": 0.5}, {"burn_rate": 5}, {"burn_rate": 15}])
    assert r["fast_burn"] == 1
    assert r["slow_burn"] == 1
    assert r["alert"]
