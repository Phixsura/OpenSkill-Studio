from app.services.app_marketplace_app_platform_status_summary import build_status_summary

def test_all_operational():
    services = [{"name": "API", "status": "operational"}, {"name": "CDN", "status": "operational"}]
    r = build_status_summary(services=services, active_incidents=0, uptime_90d=99.99, last_incident_days_ago=30)
    assert r["overall_status"] == "all_operational"
    assert r["operational"] == 2

def test_partial():
    services = [{"name": "API", "status": "operational"}, {"name": "Search", "status": "degraded"}]
    r = build_status_summary(services=services, active_incidents=0, uptime_90d=99.5, last_incident_days_ago=5)
    assert r["overall_status"] == "partial_outage"

def test_major():
    services = [{"name": "DB", "status": "outage"}]
    r = build_status_summary(services=services, active_incidents=1, uptime_90d=98.0, last_incident_days_ago=0)
    assert r["overall_status"] == "major_outage"
    assert r["down"] == 1
