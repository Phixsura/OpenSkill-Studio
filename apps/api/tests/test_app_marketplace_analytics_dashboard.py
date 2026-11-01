from app.services.app_marketplace_analytics_dashboard import build_analytics_dashboard

def test_dashboard():
    d = build_analytics_dashboard(
        app_id="app1",
        installs=[{"status": "active"}, {"status": "active"}, {"status": "uninstalled"}],
        events=[{"event_type": "webhook"}, {"event_type": "webhook"}, {"event_type": "api_call"}],
        errors=[{"type": "timeout"}])
    assert d["installs"]["total"] == 3
    assert d["installs"]["active"] == 2
    assert d["installs"]["churn_rate"] > 0
    assert d["events"]["total"] == 3
    assert d["errors"]["rate"] > 0

def test_empty():
    d = build_analytics_dashboard(app_id="x", installs=[], events=[], errors=[])
    assert d["installs"]["total"] == 0
    assert d["errors"]["rate"] == 0
