from app.services.app_marketplace_app_app_app_app_app_app_app_retry_policy import (
    create_policy, compute_delay, should_retry,
)

def test_exponential():
    p = create_policy(max_retries=3, backoff="exponential", base_delay_ms=1000)
    d0 = compute_delay(p, 0)
    assert d0["delay_ms"] == 1000
    d1 = compute_delay(p, 1)
    assert d1["delay_ms"] == 2000
    d2 = compute_delay(p, 2)
    assert d2["delay_ms"] == 4000
    d3 = compute_delay(p, 3)
    assert not d3["should_retry"]

def test_should_retry():
    p = create_policy(max_retries=2)
    assert should_retry(p, 503, 0)["retry"]
    assert not should_retry(p, 404, 0)["retry"]
    assert not should_retry(p, 503, 2)["retry"]
