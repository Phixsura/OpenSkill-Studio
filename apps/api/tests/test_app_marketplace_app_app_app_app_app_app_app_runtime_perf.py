from app.services.app_marketplace_app_app_app_app_app_app_app_runtime_perf import profile_runtime

def test_healthy():
    r = profile_runtime({"gc_pause_ms": 5, "heap_used_mb": 256, "heap_total_mb": 512,
                           "event_loop_lag_ms": 2, "active_handles": 50})
    assert r["health"] == "healthy"
    assert len(r["issues"]) == 0
    assert r["heap_pct"] == 50.0

def test_critical():
    r = profile_runtime({"gc_pause_ms": 200, "heap_used_mb": 480, "heap_total_mb": 512,
                           "event_loop_lag_ms": 100})
    assert r["health"] == "critical"
    assert len(r["issues"]) == 3
