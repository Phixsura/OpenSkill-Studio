from app.services.app_marketplace_app_app_app_app_app_app_app_health_pulse import compute_pulse

def test_healthy():
    r = compute_pulse(api_ok=True, db_ok=True, cache_ok=True, queue_ok=True, storage_ok=True,
                       error_rate_pct=0.1, p99_latency_ms=85)
    assert r["status"] == "healthy"
    assert r["score"] == 100
    assert r["emoji"] == "💚"

def test_degraded():
    r = compute_pulse(api_ok=True, db_ok=True, cache_ok=False, queue_ok=True, storage_ok=True)
    assert r["status"] == "degraded"
    assert r["score"] == 80

def test_critical():
    r = compute_pulse(api_ok=True, db_ok=True, cache_ok=True, queue_ok=True, storage_ok=True,
                       active_incidents=2, error_rate_pct=8)
    assert r["status"] == "critical"
