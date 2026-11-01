from app.services.app_marketplace_app_app_app_app_app_app_app_perf_budget import create_budget, check_budget, trend_budgets

def test_check():
    b = create_budget("Web Vitals", {"lcp_ms": 2500, "fid_ms": 100, "cls": 0.1})
    r = check_budget(b, {"lcp_ms": 2200, "fid_ms": 150, "cls": 0.05})
    assert r["violations"] == 1  # fid over
    assert not r["within_budget"]

def test_within():
    b = create_budget("API", {"p99_ms": 500})
    r = check_budget(b, {"p99_ms": 300})
    assert r["within_budget"]

def test_trend():
    history = [{"violations": 3}, {"violations": 2}, {"violations": 1}]
    r = trend_budgets(history)
    assert r["improving"]
    assert r["trend"] == "improving"
