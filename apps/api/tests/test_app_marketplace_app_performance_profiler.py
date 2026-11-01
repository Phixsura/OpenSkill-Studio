from app.services.app_marketplace_app_performance_profiler import profile_endpoints

def test_profile():
    eps = [
        {"path": "/api/apps", "method": "GET", "p50_ms": 30, "p95_ms": 80, "p99_ms": 150, "requests_per_sec": 100},
        {"path": "/api/search", "method": "GET", "p50_ms": 200, "p95_ms": 800, "p99_ms": 1500, "requests_per_sec": 50},
    ]
    r = profile_endpoints(endpoints=eps)
    assert r["total"] == 2
    assert r["slow_endpoints"] == 1
    assert r["endpoints"][0]["endpoint"] == "/api/search"  # sorted by p95 desc
    assert r["overall_score"] == 85

def test_all_fast():
    eps = [{"path": "/health", "p50_ms": 5, "p95_ms": 10, "p99_ms": 20}]
    r = profile_endpoints(endpoints=eps)
    assert r["slow_endpoints"] == 0
    assert r["overall_score"] == 100
