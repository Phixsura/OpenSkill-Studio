from app.services.app_marketplace_app_request_logger import log_request, summarize_requests

def test_log():
    r = log_request(method="GET", path="/api/apps", status_code=200, latency_ms=45, user_id="u1")
    assert r["request_id"].startswith("req_")
    assert r["level"] == "info"

def test_log_error():
    r = log_request(method="POST", path="/api/x", status_code=500, latency_ms=2000)
    assert r["level"] == "error"

def test_summary():
    logs = [
        {"method": "GET", "status_code": 200, "latency_ms": 30},
        {"method": "GET", "status_code": 200, "latency_ms": 50},
        {"method": "POST", "status_code": 500, "latency_ms": 3000},
    ]
    r = summarize_requests(logs=logs)
    assert r["total_requests"] == 3
    assert r["error_count"] == 1
    assert r["by_method"]["GET"] == 2
