from app.services.app_marketplace_app_app_health_summary import compute_health_summary

def test_excellent():
    r = compute_health_summary(uptime_pct=99.99, error_rate=0.01, latency_p95_ms=50,
        crash_free_pct=99.9, satisfaction_pct=95)
    assert r["status"] == "excellent"
    assert r["overall_score"] > 95

def test_poor():
    r = compute_health_summary(uptime_pct=90, error_rate=10, latency_p95_ms=2000,
        crash_free_pct=85, satisfaction_pct=40)
    assert r["status"] in ("fair", "poor")
    assert r["overall_score"] < 80

def test_signals():
    r = compute_health_summary(uptime_pct=100, error_rate=0, latency_p95_ms=0,
        crash_free_pct=100, satisfaction_pct=100)
    assert r["overall_score"] == 100
    assert all(v == 100 for v in r["signals"].values())
