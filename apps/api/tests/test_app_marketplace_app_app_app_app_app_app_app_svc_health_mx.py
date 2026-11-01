from app.services.app_marketplace_app_app_app_app_app_app_app_svc_health_mx import build_health_matrix, identify_weakest

def test_matrix():
    r = build_health_matrix([
        {"name": "api", "uptime_pct": 99.99, "p99_ms": 100, "error_rate": 0.1, "cpu_pct": 40},
        {"name": "worker", "uptime_pct": 99.5, "p99_ms": 800, "error_rate": 3, "cpu_pct": 90},
    ])
    assert r["healthy"] == 1
    assert r["health_pct"] == 50

def test_weakest():
    m = build_health_matrix([
        {"name": "a", "uptime_pct": 100, "p99_ms": 50, "error_rate": 0, "cpu_pct": 30},
        {"name": "b", "uptime_pct": 95, "p99_ms": 1000, "error_rate": 5, "cpu_pct": 95},
    ])
    w = identify_weakest(m)
    assert w["weakest"] == "b"
    assert len(w["failed_dimensions"]) >= 3
