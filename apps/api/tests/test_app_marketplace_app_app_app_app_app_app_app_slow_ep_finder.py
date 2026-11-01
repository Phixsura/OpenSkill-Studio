from app.services.app_marketplace_app_app_app_app_app_app_app_slow_ep_finder import find_slow_endpoints

def test_find():
    reqs = [{"endpoint": "/fast", "latency_ms": 20}] * 100
    reqs += [{"endpoint": "/slow", "latency_ms": 50}] * 90
    reqs += [{"endpoint": "/slow", "latency_ms": 500}] * 10
    r = find_slow_endpoints(reqs, threshold_ms=200)
    assert r["slow_count"] == 1
    assert r["slow_endpoints"][0]["endpoint"] == "/slow"
    assert r["total_endpoints"] == 2
