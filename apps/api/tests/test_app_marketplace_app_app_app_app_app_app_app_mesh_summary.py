from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_summary import mesh_summary

def test_healthy():
    r = mesh_summary(
        [{"name": "api", "healthy": True, "mtls": True},
         {"name": "db", "healthy": True, "mtls": True}],
        {"total_rps": 5000, "error_rate_pct": 0.1},
        {"avg_latency_ms": 45})
    assert r["overall"] == "healthy"
    assert r["mtls_coverage_pct"] == 100.0

def test_degraded():
    r = mesh_summary(
        [{"name": "api", "healthy": True, "mtls": True},
         {"name": "db", "healthy": False, "mtls": False}],
        {"total_rps": 3000, "error_rate_pct": 5},
        {"avg_latency_ms": 200})
    assert r["overall"] == "degraded"
