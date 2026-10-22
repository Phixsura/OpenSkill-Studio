from app.services.app_developer_api_status import build_api_status, DEFAULT_SERVICES

def test_all_operational():
    s = build_api_status(services=DEFAULT_SERVICES)
    assert s["overall"] == "operational"
    assert s["uptime_pct"] > 99

def test_degraded():
    svc = [{"name": "API", "status": "degraded", "uptime_pct": 95}]
    s = build_api_status(services=svc)
    assert s["overall"] == "degraded"

def test_outage():
    svc = [{"name": "API", "status": "outage", "uptime_pct": 50}]
    s = build_api_status(services=svc)
    assert s["overall"] == "outage"

def test_default_services():
    assert len(DEFAULT_SERVICES) >= 5
