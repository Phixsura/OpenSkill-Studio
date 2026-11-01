from app.services.app_marketplace_app_app_retry_policy import calculate_backoff, build_retry_schedule

def test_backoff_increases():
    d0 = calculate_backoff(attempt=0, jitter=False)
    d3 = calculate_backoff(attempt=3, jitter=False)
    assert d3["delay_s"] > d0["delay_s"]

def test_backoff_capped():
    r = calculate_backoff(attempt=100, base_delay_s=1.0, max_delay_s=60.0, jitter=False)
    assert r["delay_s"] == 60.0
    assert r["capped"]

def test_schedule():
    r = build_retry_schedule(max_attempts=4, base_delay_s=1.0, max_delay_s=30.0)
    assert r["max_attempts"] == 4
    assert len(r["schedule"]) == 4
    assert r["schedule"][0]["delay_s"] == 1.0
    assert r["schedule"][1]["delay_s"] == 2.0
    assert r["schedule"][2]["delay_s"] == 4.0
    assert r["total_wait_s"] == 15.0
