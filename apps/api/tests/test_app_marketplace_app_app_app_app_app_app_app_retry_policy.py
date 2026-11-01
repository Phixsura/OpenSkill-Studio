from app.services.app_marketplace_app_app_app_app_app_app_app_retry_policy import calculate_delay, should_retry, retry_budget

def test_exponential():
    r1 = calculate_delay(1, base_ms=1000)
    assert r1["delay_ms"] == 1000
    r2 = calculate_delay(3, base_ms=1000)
    assert r2["delay_ms"] == 4000
    r3 = calculate_delay(10, base_ms=1000, max_ms=30000)
    assert r3["capped"]

def test_should_retry():
    assert should_retry(503, 1)["retry"]
    assert not should_retry(404, 1)["retry"]
    assert not should_retry(503, 3, max_attempts=3)["retry"]

def test_budget():
    r = retry_budget(10000, 500, budget_pct=10)
    assert r["budget"] == 1000
    assert r["remaining"] == 500
    assert not r["exhausted"]
