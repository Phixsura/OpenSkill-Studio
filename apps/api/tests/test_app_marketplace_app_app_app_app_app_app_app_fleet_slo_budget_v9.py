from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_slo_budget_v9 import fleet_slo_budget_v9
def test_slo_v9():
    r = fleet_slo_budget_v9([{"budget_remaining_pct": 85}, {"budget_remaining_pct": 92}])
    assert r["compliant"] == 2
    assert r["burned"] == 0
    assert r["healthy"]
