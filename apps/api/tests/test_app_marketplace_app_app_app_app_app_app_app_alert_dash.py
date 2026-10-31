from app.services.app_marketplace_app_app_app_app_app_app_app_alert_dash import build_alert_dashboard, group_by_service

def test_dashboard():
    r = build_alert_dashboard([
        {"status": "firing", "severity": "critical", "service": "db"},
        {"status": "firing", "severity": "warning", "service": "api"},
        {"status": "resolved", "severity": "warning", "service": "api"},
    ])
    assert r["active"] == 2
    assert r["status"] == "critical"
    assert r["critical_count"] == 1

def test_group():
    alerts = [{"service": "api"}, {"service": "api"}, {"service": "db"}]
    r = group_by_service(alerts)
    assert r["most_alerts"] == "api"
    assert r["services"]["api"] == 2
