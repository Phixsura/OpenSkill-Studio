from app.services.app_marketplace_app_app_app_app_app_app_app_endpoint_health import build_health_matrix

def test_matrix():
    r = build_health_matrix([
        {"path": "/users", "method": "GET", "p99_ms": 100, "slo_ms": 500, "error_rate": 0.1, "rpm": 1000},
        {"path": "/orders", "method": "POST", "p99_ms": 800, "slo_ms": 500, "error_rate": 3, "rpm": 200},
        {"path": "/legacy", "method": "GET", "p99_ms": 2000, "slo_ms": 500, "error_rate": 8, "rpm": 50},
    ])
    assert r["healthy"] == 1
    assert r["degraded"] == 1
    assert r["unhealthy"] == 1
    assert r["health_pct"] == 33
