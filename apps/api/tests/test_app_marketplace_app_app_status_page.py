from app.services.app_marketplace_app_app_status_page import build_status_page

def test_all_operational():
    svcs = [{"name": "API", "status": "operational", "uptime_pct": 99.99},
            {"name": "Web", "status": "operational", "uptime_pct": 99.95}]
    r = build_status_page(services=svcs)
    assert r["overall"] == "operational"
    assert r["overall_icon"] == "🟢"
    assert len(r["services"]) == 2

def test_degraded():
    svcs = [{"name": "API", "status": "degraded"}, {"name": "DB", "status": "operational"}]
    r = build_status_page(services=svcs)
    assert r["overall"] == "degraded"

def test_outage_wins():
    svcs = [{"name": "API", "status": "outage"}, {"name": "DB", "status": "degraded"}]
    r = build_status_page(services=svcs)
    assert r["overall"] == "outage"

def test_incidents():
    r = build_status_page(services=[], incidents=[{"title": "DB slow", "status": "investigating"}])
    assert len(r["incidents"]) == 1
