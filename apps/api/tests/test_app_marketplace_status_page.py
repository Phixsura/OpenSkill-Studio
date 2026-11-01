from app.services.app_marketplace_status_page import build_status_page, build_service_status, build_uptime_bars

def test_all_ok():
    services = [{"name": "API", "status": "operational"}, {"name": "Webhooks", "status": "operational"}]
    p = build_status_page(services=services, incidents=[])
    assert p["overall_status"] == "all_operational"

def test_partial():
    services = [{"name": "API", "status": "operational"}, {"name": "Webhooks", "status": "degraded"}]
    p = build_status_page(services=services, incidents=[])
    assert p["overall_status"] == "partial_outage"

def test_service_operational():
    s = build_service_status(name="API", uptime_pct=99.95, response_time_ms=120)
    assert s["status"] == "operational"

def test_service_degraded():
    s = build_service_status(name="API", uptime_pct=99.5, response_time_ms=500)
    assert s["status"] == "degraded"

def test_bars():
    daily = [{"date": "2026-01-01", "uptime_pct": 100}, {"date": "2026-01-02", "uptime_pct": 98}]
    bars = build_uptime_bars(daily_uptimes=daily)
    assert bars[0]["color"] == "green"
    assert bars[1]["color"] == "red"
