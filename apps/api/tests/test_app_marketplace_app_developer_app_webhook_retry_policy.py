from app.services.app_marketplace_app_developer_app_webhook_retry_policy import create_retry_policy, compute_retry_delay, build_retry_schedule, should_retry

def test_create():
    p = create_retry_policy(max_retries=3, initial_delay_ms=500)
    assert p["max_retries"] == 3

def test_invalid():
    p = create_retry_policy(max_retries=50)
    assert p["error"]

def test_delay():
    policy = {"initial_delay_ms": 1000, "backoff_multiplier": 2.0, "max_delay_ms": 60000}
    assert compute_retry_delay(attempt=0, policy=policy) == 1000
    assert compute_retry_delay(attempt=1, policy=policy) == 2000
    assert compute_retry_delay(attempt=2, policy=policy) == 4000

def test_max_delay():
    policy = {"initial_delay_ms": 1000, "backoff_multiplier": 10.0, "max_delay_ms": 5000}
    assert compute_retry_delay(attempt=5, policy=policy) == 5000

def test_schedule():
    policy = create_retry_policy(max_retries=3, initial_delay_ms=1000)
    s = build_retry_schedule(policy=policy)
    assert len(s) == 3
    assert s[0]["delay_ms"] == 1000

def test_should_retry_500():
    r = should_retry(status_code=500, attempt=1, max_retries=5)
    assert r["should_retry"]

def test_should_not_retry_400():
    r = should_retry(status_code=400, attempt=1, max_retries=5)
    assert not r["should_retry"]

def test_exhausted():
    r = should_retry(status_code=500, attempt=5, max_retries=5)
    assert not r["should_retry"]
