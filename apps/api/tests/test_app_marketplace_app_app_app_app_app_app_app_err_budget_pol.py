from app.services.app_marketplace_app_app_app_app_app_app_app_err_budget_pol import evaluate_budget_policy, budget_forecast

def test_triggered():
    r = evaluate_budget_policy(85, [
        {"name": "slow_down", "threshold_pct": 70, "action": "reduce_deploy_frequency", "severity": "warning"},
        {"name": "freeze", "threshold_pct": 90, "action": "freeze_deploys", "severity": "critical"},
    ])
    assert len(r["triggered_policies"]) == 1
    assert r["recommended_action"] == "reduce_deploy_frequency"
    assert not r["freeze_deploys"]

def test_exhausted():
    r = evaluate_budget_policy(100, [
        {"name": "freeze", "threshold_pct": 90, "action": "freeze_deploys"},
    ])
    assert r["freeze_deploys"]

def test_forecast():
    r = budget_forecast(50, 5.0, 15)
    assert r["will_exhaust"]
    assert r["days_to_exhaustion"] == 10
