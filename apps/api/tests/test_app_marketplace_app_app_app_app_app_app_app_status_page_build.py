from app.services.app_marketplace_app_app_app_app_app_app_app_status_page_build import build_status_page

def test_all_operational():
    r = build_status_page("MyApp", [
        {"name": "API", "status": "operational", "uptime_pct": 99.99},
        {"name": "Web", "status": "operational", "uptime_pct": 99.95},
    ])
    assert r["overall"] == "operational"
    assert r["avg_uptime"] == 99.97

def test_with_outage():
    r = build_status_page("App", [
        {"name": "API", "status": "operational"},
        {"name": "DB", "status": "outage"},
    ])
    assert r["overall"] == "outage"
    assert r["summary"]["outage"] == 1
