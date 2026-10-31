from app.services.app_marketplace_app_app_performance_budget import check_budget, summarize_budget

def test_within_budget():
    r = check_budget(metrics={"js_kb": 150, "css_kb": 30, "lcp_ms": 2000})
    assert r["within_budget"]
    assert r["violations"] == 0

def test_over_budget():
    r = check_budget(metrics={"js_kb": 300, "lcp_ms": 3500},
                     budget={"js_kb": 200, "lcp_ms": 2500})
    assert not r["within_budget"]
    assert r["violations"] == 2

def test_summarize():
    r = summarize_budget(metrics={"js_kb": 200, "css_kb": 50, "image_kb": 300})
    assert r["total_transfer_kb"] == 550
