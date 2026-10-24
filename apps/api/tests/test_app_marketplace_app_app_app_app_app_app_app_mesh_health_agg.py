from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_health_agg import aggregate_mesh_health

def test_healthy():
    r = aggregate_mesh_health([
        {"name": "api", "health": "healthy", "avg_latency_ms": 50, "error_rate_pct": 0.1, "mtls": True},
        {"name": "db", "health": "healthy", "avg_latency_ms": 5, "error_rate_pct": 0, "mtls": True},
    ])
    assert r["overall"] == "healthy"
    assert r["health_pct"] == 100.0
    assert r["mtls_coverage_pct"] == 100.0

def test_degraded():
    r = aggregate_mesh_health([
        {"name": "api", "health": "healthy", "avg_latency_ms": 50, "error_rate_pct": 0.1, "mtls": True},
        {"name": "db", "health": "down", "avg_latency_ms": 0, "error_rate_pct": 100, "mtls": False},
    ])
    assert r["overall"] == "degraded"
    assert r["down"] == 1
