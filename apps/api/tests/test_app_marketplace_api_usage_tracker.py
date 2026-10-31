from app.services.app_marketplace_api_usage_tracker import track_api_call, compute_usage_summary, check_rate_limit

def test_track():
    calls = track_api_call(app_id="a1", endpoint="/api/v1/data", method="GET",
                            status_code=200, response_time_ms=50, calls=[])
    assert len(calls) == 1
    assert calls[0]["endpoint"] == "/api/v1/data"

def test_summary():
    calls = [{"endpoint": "/a", "status_code": 200, "response_time_ms": 100},
             {"endpoint": "/a", "status_code": 200, "response_time_ms": 200},
             {"endpoint": "/b", "status_code": 500, "response_time_ms": 50}]
    s = compute_usage_summary(calls=calls, quota=1000)
    assert s["total_calls"] == 3
    assert s["usage_pct"] == 0.3
    assert s["by_endpoint"]["/a"] == 2

def test_rate_limit_ok():
    r = check_rate_limit(app_id="a1", window_calls=50, limit=100)
    assert r["allowed"]
    assert r["remaining"] == 50

def test_rate_limit_exceeded():
    r = check_rate_limit(app_id="a1", window_calls=100, limit=100)
    assert not r["allowed"]
    assert r["retry_after"] == 60
