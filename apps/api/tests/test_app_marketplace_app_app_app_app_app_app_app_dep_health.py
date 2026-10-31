from app.services.app_marketplace_app_app_app_app_app_app_app_dep_health import check_dependencies

def test_all_healthy():
    r = check_dependencies([
        {"name": "db", "status": "healthy", "latency_ms": 5, "critical": True},
        {"name": "cache", "status": "healthy", "latency_ms": 1},
    ])
    assert r["overall"] == "healthy"
    assert r["down"] == 0

def test_critical_down():
    r = check_dependencies([
        {"name": "db", "status": "down", "latency_ms": 0, "critical": True},
        {"name": "cache", "status": "healthy", "latency_ms": 1},
    ])
    assert r["overall"] == "critical"
    assert r["critical_down"] == 1

def test_degraded():
    r = check_dependencies([
        {"name": "api", "status": "healthy", "latency_ms": 1000, "latency_threshold_ms": 500},
    ])
    assert r["degraded"] == 1
    assert r["overall"] == "degraded"
