from app.services.app_marketplace_app_app_app_app_app_app_app_err_budget import calculate_budget, budget_trend

def test_ok():
    r = calculate_budget(0.999, 1000000, 500)
    assert r["budget_total"] == 1000
    assert r["pct_consumed"] == 50.0
    assert r["status"] == "ok"

def test_exhausted():
    r = calculate_budget(0.999, 1000000, 1500)
    assert r["status"] == "exhausted"

def test_trend():
    r = budget_trend([{"pct_consumed": 30}, {"pct_consumed": 40}, {"pct_consumed": 50}])
    assert r["trend"] == "worsening"
