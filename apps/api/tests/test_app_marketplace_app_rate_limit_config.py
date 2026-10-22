from app.services.app_marketplace_app_rate_limit_config import create_rate_limit_rule, evaluate_rate_limit

def test_create():
    r = create_rate_limit_rule(app_id="a1", endpoint="/api/data", requests_per_minute=100)
    assert r["requests_per_minute"] == 100
    assert r["burst"] == 200

def test_too_low():
    r = create_rate_limit_rule(app_id="a1", endpoint="/api", requests_per_minute=0)
    assert r["error"]

def test_too_high():
    r = create_rate_limit_rule(app_id="a1", endpoint="/api", requests_per_minute=99999)
    assert r["error"]

def test_evaluate_allowed():
    rule = {"requests_per_minute": 100}
    r = evaluate_rate_limit(rule=rule, current_count=50, window_start_epoch=1000, now_epoch=1030)
    assert r["allowed"]
    assert r["remaining"] == 50

def test_evaluate_exceeded():
    rule = {"requests_per_minute": 100}
    r = evaluate_rate_limit(rule=rule, current_count=100, window_start_epoch=1000, now_epoch=1030)
    assert not r["allowed"]
    assert r["retry_after"] == 30
