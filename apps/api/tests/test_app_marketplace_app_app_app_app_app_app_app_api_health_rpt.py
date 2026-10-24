from app.services.app_marketplace_app_app_app_app_app_app_app_api_health_rpt import generate_api_report

def test_report():
    r = generate_api_report([
        {"path": "/users", "rps": 500, "p99_ms": 100, "error_rate": 0.1},
        {"path": "/orders", "rps": 200, "p99_ms": 250, "error_rate": 0.5},
        {"path": "/legacy", "rps": 50, "p99_ms": 800, "error_rate": 3},
    ])
    assert r["healthy"] == 2
    assert r["degraded"] == 1
    assert r["total_rps"] == 750
    assert r["grade"] in ("A", "B")
