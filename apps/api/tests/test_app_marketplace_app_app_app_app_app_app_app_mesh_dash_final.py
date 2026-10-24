from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_dash_final import mesh_dashboard_final

def test_healthy():
    r = mesh_dashboard_final({
        "services": [{"healthy": True, "mtls": True}] * 10,
        "total_rps": 5000, "error_rate_pct": 0.1, "p99_ms": 100,
        "circuit_trips": 0, "total_retries": 50})
    assert r["status"] == "healthy"
    assert r["score"] == 100

def test_issues():
    r = mesh_dashboard_final({
        "services": [{"healthy": True, "mtls": True}] * 8 + [{"healthy": False, "mtls": False}] * 2,
        "total_rps": 3000, "error_rate_pct": 5, "p99_ms": 800,
        "circuit_trips": 3, "total_retries": 500})
    assert r["status"] != "healthy"
    assert r["score"] < 80
