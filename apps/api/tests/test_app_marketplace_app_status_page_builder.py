from app.services.app_marketplace_app_status_page_builder import build_status_page, get_uptime_bars

def test_all_operational():
    comps = [{"name": "API", "status": "operational"}, {"name": "Web", "status": "operational"}]
    r = build_status_page(app_name="MyApp", components=comps)
    assert r["overall_status"] == "operational"

def test_degraded():
    comps = [{"name": "API", "status": "operational"}, {"name": "CDN", "status": "degraded"}]
    r = build_status_page(app_name="MyApp", components=comps)
    assert r["overall_status"] == "degraded"

def test_major():
    comps = [{"name": "DB", "status": "major_outage"}]
    r = build_status_page(app_name="MyApp", components=comps)
    assert r["overall_status"] == "major_outage"

def test_uptime():
    r = get_uptime_bars(days=90)
    assert len(r["bars"]) == 90
    assert r["average_uptime"] > 99.0
