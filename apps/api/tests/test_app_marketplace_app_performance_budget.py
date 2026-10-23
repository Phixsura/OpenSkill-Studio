from app.services.app_marketplace_app_performance_budget import check_budget

def test_within():
    actuals = {"js_size_kb": 250, "css_size_kb": 80, "lcp_ms": 2000}
    r = check_budget(actuals=actuals)
    assert r["all_within_budget"]
    assert r["violations"] == 0

def test_over():
    actuals = {"js_size_kb": 500, "lcp_ms": 4000, "cls": 0.05}
    r = check_budget(actuals=actuals)
    assert not r["all_within_budget"]
    assert r["violations"] == 2  # js and lcp

def test_custom():
    r = check_budget(budgets={"js_size_kb": 100}, actuals={"js_size_kb": 150})
    assert r["violations"] == 1
    assert r["results"][0]["overage"] == 50
