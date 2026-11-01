from app.services.app_marketplace_app_api_usage_tracker import track_api_call, get_usage_report

def test_track():
    r = track_api_call(endpoint="/api/apps", method="GET", status_code=200,
        latency_ms=45, api_key_prefix="sk_abc")
    assert r["success"]
    assert r["method"] == "GET"

def test_report():
    calls = [
        {"method": "GET", "endpoint": "/api/apps", "status_code": 200, "latency_ms": 30, "success": True},
        {"method": "GET", "endpoint": "/api/apps", "status_code": 200, "latency_ms": 50, "success": True},
        {"method": "POST", "endpoint": "/api/apps", "status_code": 500, "latency_ms": 2000, "success": False},
    ]
    r = get_usage_report(calls=calls)
    assert r["total_calls"] == 3
    assert r["success_rate"] == 66.7
    assert r["endpoints"][0]["endpoint"] == "GET /api/apps"
    assert r["endpoints"][0]["count"] == 2
