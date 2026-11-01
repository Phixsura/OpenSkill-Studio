from app.services.app_marketplace_health_report import build_marketplace_health

def test_healthy():
    r = build_marketplace_health(total_apps=100, healthy_pct=98, avg_latency_ms=80, webhook_success_pct=99.5, active_developers=20)
    assert r["status"] == "healthy"
    assert r["grade"] == "A"

def test_degraded():
    r = build_marketplace_health(total_apps=100, healthy_pct=85, avg_latency_ms=200, webhook_success_pct=95, active_developers=10)
    assert r["status"] == "degraded"

def test_critical():
    r = build_marketplace_health(total_apps=50, healthy_pct=60, avg_latency_ms=500, webhook_success_pct=80, active_developers=5)
    assert r["status"] == "critical"
    assert r["grade"] == "C"
