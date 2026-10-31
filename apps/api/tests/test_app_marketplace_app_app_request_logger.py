from app.services.app_marketplace_app_app_request_logger import log_request, analyze_requests

def test_log():
    r = log_request(method="GET", path="/api/v1/apps", status_code=200, duration_ms=45)
    assert r["method"] == "GET"
    assert r["success"]

def test_analyze():
    logs = [
        {"path": "/api/apps", "status_code": 200, "duration_ms": 50},
        {"path": "/api/apps", "status_code": 200, "duration_ms": 60},
        {"path": "/api/users", "status_code": 500, "duration_ms": 200},
    ]
    r = analyze_requests(logs=logs)
    assert r["total"] == 3
    assert r["error_rate"] == 33.3
    assert r["top_paths"][0]["path"] == "/api/apps"

def test_empty():
    r = analyze_requests(logs=[])
    assert r["total"] == 0
