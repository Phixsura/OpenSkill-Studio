from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tfc import fleet_tfc_status
def test_tfc():
    r = fleet_tfc_status([{"last_run": "applied", "monthly_cost_usd": 5000}, {"last_run": "errored", "monthly_cost_usd": 3000}])
    assert r["applied"] == 1
    assert r["errored"] == 1
    assert not r["healthy"]
