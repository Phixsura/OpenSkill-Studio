from app.services.app_marketplace_app_developer_app_api_latency_profiler import compute_latency_percentiles, identify_slow_endpoints, compute_latency_budget

def test_percentiles():
    lats = list(range(1, 101))  # 1-100ms
    r = compute_latency_percentiles(latencies=lats)
    assert r["p50"] == 51
    assert r["p99"] == 100
    assert r["avg"] == 50

def test_empty():
    r = compute_latency_percentiles(latencies=[])
    assert r["p50"] == 0

def test_slow_endpoints():
    endpoints = {"/users": [100, 200, 300], "/heavy": [500, 800, 1200]}
    r = identify_slow_endpoints(endpoint_latencies=endpoints, threshold_ms=500)
    assert len(r) == 1
    assert r[0]["path"] == "/heavy"

def test_budget_ok():
    r = compute_latency_budget(target_p99_ms=500, current_p99_ms=300)
    assert r["within_budget"]
    assert r["remaining_ms"] == 200

def test_budget_exceeded():
    r = compute_latency_budget(target_p99_ms=200, current_p99_ms=500)
    assert not r["within_budget"]
