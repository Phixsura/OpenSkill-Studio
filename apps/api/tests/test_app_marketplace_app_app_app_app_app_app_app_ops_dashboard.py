from app.services.app_marketplace_app_app_app_app_app_app_app_ops_dashboard import build_ops_dashboard

def test_healthy():
    r = build_ops_dashboard({
        "health": {"uptime_pct": 99.99},
        "traffic": {"rps": 5000, "error_rate_pct": 0.1, "p99_ms": 100},
        "incidents": {"active": 0},
        "deployments": {"today": 3},
        "services_count": 50})
    assert r["status"] == "healthy"
    assert r["score"] == 100

def test_degraded():
    r = build_ops_dashboard({
        "health": {"uptime_pct": 99.5},
        "traffic": {"rps": 3000, "error_rate_pct": 5, "p99_ms": 800},
        "incidents": {"active": 3},
        "deployments": {"today": 0},
        "services_count": 50})
    assert r["status"] == "degraded"
    assert r["score"] < 80
