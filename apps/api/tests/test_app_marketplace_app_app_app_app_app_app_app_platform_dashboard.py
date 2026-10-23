from app.services.app_marketplace_app_app_app_app_app_app_app_platform_dashboard import build_dashboard_summary

def test_dashboard():
    r = build_dashboard_summary(
        apps=250, developers=1500, api_calls_24h=2500000,
        uptime_pct=99.95, revenue_mrr=45000, active_webhooks=340,
        error_rate_pct=0.3, avg_latency_ms=85, deployments_today=12,
        open_incidents=0
    )
    assert r["health_score"] == 100
    assert r["status"] == "excellent"
    assert r["metrics"]["apps"]["display"] == "250"
    assert r["metrics"]["mrr"]["display"] == "$45,000"
    assert r["metrics"]["api_calls_24h"]["display"] == "2,500,000"
    assert "2,100" in r["milestone"]

def test_degraded():
    r = build_dashboard_summary(uptime_pct=99.0, error_rate_pct=2.5, open_incidents=3)
    assert r["health_score"] < 50
    assert r["status"] == "poor"
