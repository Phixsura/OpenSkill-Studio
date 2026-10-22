from app.services.app_marketplace_app_error_budget import compute_error_budget, get_burn_rate, recommend_action

def test_healthy():
    r = compute_error_budget(slo_target=99.9, total_requests=100000, failed_requests=10)
    assert not r["budget_exhausted"]
    assert r["budget_remaining"] > 0

def test_exhausted():
    r = compute_error_budget(slo_target=99.9, total_requests=100000, failed_requests=200)
    assert r["budget_exhausted"]

def test_burn_rate_ok():
    r = get_burn_rate(budget_remaining_pct=70, elapsed_pct=30)
    assert r["on_track"]
    assert r["alert"] is None

def test_burn_rate_critical():
    r = get_burn_rate(budget_remaining_pct=20, elapsed_pct=30)
    assert r["burn_rate"] > 2

def test_recommend_freeze():
    assert "FREEZE" in recommend_action(budget_pct=0, burn_rate=3)

def test_recommend_ok():
    assert "OK" in recommend_action(budget_pct=80, burn_rate=0.8)
