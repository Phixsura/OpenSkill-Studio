from app.services.app_marketplace_app_request_inspector import capture_request, search_requests, compute_request_stats

def test_capture():
    r = capture_request(method="GET", path="/api/v1/apps", headers={"Authorization": "Bearer secret", "Accept": "application/json"},
                         status_code=200, duration_ms=45)
    assert "Authorization" not in r["headers"]
    assert r["duration_ms"] == 45

def test_search_status():
    reqs = [{"status_code": 200, "method": "GET", "path": "/a"},
            {"status_code": 500, "method": "POST", "path": "/b"}]
    assert len(search_requests(requests=reqs, status_filter=500)) == 1

def test_search_method():
    reqs = [{"method": "GET", "path": "/a"}, {"method": "POST", "path": "/b"}]
    assert len(search_requests(requests=reqs, method_filter="post")) == 1

def test_stats():
    reqs = [{"status_code": 200, "duration_ms": 100}, {"status_code": 500, "duration_ms": 200}]
    s = compute_request_stats(requests=reqs)
    assert s["error_rate"] == 50.0
    assert s["avg_duration_ms"] == 150
