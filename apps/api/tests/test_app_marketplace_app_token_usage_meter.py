from app.services.app_marketplace_app_token_usage_meter import calculate_token_usage, check_token_budget

def test_usage():
    requests = [
        {"input_tokens": 500, "output_tokens": 200},
        {"input_tokens": 1000, "output_tokens": 500},
    ]
    r = calculate_token_usage(requests=requests)
    assert r["total_tokens"] == 2200
    assert r["total_requests"] == 2
    assert r["estimated_cost"] > 0

def test_empty():
    r = calculate_token_usage(requests=[])
    assert r["total_tokens"] == 0
    assert r["estimated_cost"] == 0

def test_budget_ok():
    r = check_token_budget(used=5000, budget=10000)
    assert not r["exceeded"]
    assert r["remaining"] == 5000

def test_budget_warning():
    r = check_token_budget(used=8500, budget=10000)
    assert r["warning"]
    assert not r["exceeded"]

def test_budget_exceeded():
    r = check_token_budget(used=12000, budget=10000)
    assert r["exceeded"]
    assert r["remaining"] == 0
