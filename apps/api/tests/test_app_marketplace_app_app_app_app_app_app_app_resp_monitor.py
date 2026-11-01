from app.services.app_marketplace_app_app_app_app_app_app_app_resp_monitor import analyze_response_times

def test_monitor():
    samples = [
        {"endpoint": "/api/users", "latency_ms": 50},
        {"endpoint": "/api/users", "latency_ms": 80},
        {"endpoint": "/api/apps", "latency_ms": 120},
        {"endpoint": "/api/apps", "latency_ms": 600},
    ]
    r = analyze_response_times(samples)
    assert r["total_samples"] == 4
    assert len(r["endpoints"]) == 2
    assert r["slowest"] == "/api/apps"
    users = next(e for e in r["endpoints"] if e["endpoint"] == "/api/users")
    assert users["status"] == "fast"
