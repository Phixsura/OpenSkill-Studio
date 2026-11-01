from app.services.app_marketplace_app_app_endpoint_monitor import check_endpoint, get_monitor_summary

def test_check():
    r = check_endpoint(url="https://api.example.com/health")
    assert r["healthy"]
    assert r["actual_status"] == 200

def test_summary():
    checks = [
        {"url": "/health", "healthy": True, "latency_ms": 30},
        {"url": "/health", "healthy": True, "latency_ms": 40},
        {"url": "/api", "healthy": False, "latency_ms": 5000},
    ]
    r = get_monitor_summary(checks=checks)
    assert r["uptime_pct"] == 66.67
    assert len(r["endpoints"]) == 2
    health_ep = next(e for e in r["endpoints"] if e["url"] == "/health")
    assert health_ep["uptime_pct"] == 100.0
