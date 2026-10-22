from app.services.app_marketplace_app_performance_budget import create_budget, check_budget, suggest_optimizations

def test_within_budget():
    b = create_budget(app_id="a1")
    r = check_budget(budget=b, actual_bundle_kb=200, actual_load_ms=1500, actual_api_calls=5)
    assert r["within_budget"]
    assert r["score"] == 100

def test_over_budget():
    b = create_budget(app_id="a1", max_bundle_kb=100)
    r = check_budget(budget=b, actual_bundle_kb=200, actual_load_ms=1500, actual_api_calls=5)
    assert not r["within_budget"]

def test_all_violated():
    b = create_budget(app_id="a1", max_bundle_kb=10, max_load_ms=100, max_api_calls=1)
    r = check_budget(budget=b, actual_bundle_kb=500, actual_load_ms=5000, actual_api_calls=20)
    assert r["score"] == 0

def test_suggestions():
    violations = [{"metric": "bundle_size"}, {"metric": "api_calls"}]
    s = suggest_optimizations(violations=violations)
    assert len(s) == 2
    assert any("splitting" in x for x in s)
