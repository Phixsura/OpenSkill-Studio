from app.services.app_marketplace_developer_status_dashboard import build_developer_status_dashboard

def test_operational():
    d = build_developer_status_dashboard(
        services=[{"name": "API", "status": "operational"}, {"name": "CDN", "status": "operational"}],
        scheduled_maintenance=[], recent_incidents=[], uptime_90d=99.99)
    assert d["overall_status"] == "operational"
    assert len(d["subscribe_options"]) == 4

def test_outage():
    d = build_developer_status_dashboard(
        services=[{"name": "API", "status": "major_outage"}],
        scheduled_maintenance=[], recent_incidents=[{"status": "investigating"}], uptime_90d=98.5)
    assert d["overall_status"] == "major_outage"
    assert len(d["active_incidents"]) == 1
