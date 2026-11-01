from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sre_metrics import fleet_sre_metrics
def test_sre():
    r = fleet_sre_metrics({"toil_pct": 20, "error_budget_remaining_pct": 60, "on_call_happiness": 4.5})
    assert r["sre_mature"]
