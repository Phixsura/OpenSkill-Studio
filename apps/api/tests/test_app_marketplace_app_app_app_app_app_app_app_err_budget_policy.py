from app.services.app_marketplace_app_app_app_app_app_app_app_err_budget_policy import create_budget, check_budget, project_burn_rate

def test_budget():
    b = create_budget(99.9, 1000000)
    assert b["allowed_errors"] == 1000

def test_check():
    b = create_budget(99.9, 1000000)
    r = check_budget(b, 500)
    assert r["consumed_pct"] == 50.0
    assert r["action"] == "normal"
    r2 = check_budget(b, 900)
    assert r2["action"] == "caution"
    r3 = check_budget(b, 1000)
    assert r3["exhausted"]
    assert r3["action"] == "freeze_deploys"

def test_burn():
    r = project_burn_rate(50, 15, 30)
    assert r["daily_burn_pct"] == 3.33
    assert r["projected_at_end"] == 100.0
    assert not r["will_exhaust"]  # exactly 100
