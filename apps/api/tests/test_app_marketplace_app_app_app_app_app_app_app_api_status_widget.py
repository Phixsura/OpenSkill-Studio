from app.services.app_marketplace_app_app_app_app_app_app_app_api_status_widget import build_api_status

def test_operational():
    r = build_api_status([
        {"endpoint": "/api/apps", "healthy": True, "latency_ms": 50},
        {"endpoint": "/api/users", "healthy": True, "latency_ms": 80},
    ])
    assert r["status"] == "operational"
    assert r["icon"] == "🟢"
    assert r["healthy"] == 2

def test_degraded():
    r = build_api_status([
        {"endpoint": "/api/apps", "healthy": True, "latency_ms": 50},
        {"endpoint": "/api/db", "healthy": False, "latency_ms": 5000},
    ])
    assert r["status"] == "degraded"
