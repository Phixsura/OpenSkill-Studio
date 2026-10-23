from app.services.app_marketplace_app_app_app_app_app_app_app_retry_policy import compute_delay, build_retry_schedule

def test_exponential():
    d1 = compute_delay(attempt=1, strategy="exponential", base_delay_ms=1000, jitter=False)
    assert d1["delay_ms"] == 1000
    d3 = compute_delay(attempt=3, strategy="exponential", base_delay_ms=1000, jitter=False)
    assert d3["delay_ms"] == 4000
    d10 = compute_delay(attempt=10, strategy="exponential", base_delay_ms=1000, max_delay_ms=30000, jitter=False)
    assert d10["capped"]

def test_schedule():
    s = build_retry_schedule(max_attempts=3, strategy="exponential", base_delay_ms=1000)
    assert len(s["schedule"]) == 3
    assert s["schedule"][0]["delay_ms"] == 1000
    assert s["schedule"][1]["delay_ms"] == 2000
    assert s["schedule"][2]["delay_ms"] == 4000
    assert s["total_wait_ms"] == 7000
