from app.services.app_marketplace_app_app_app_app_app_app_app_status_page import generate_status_page, uptime_bars

def test_all_operational():
    r = generate_status_page([
        {"name": "API", "status": "operational", "group": "Core"},
        {"name": "Dashboard", "status": "operational", "group": "Web"},
    ])
    assert r["overall"] == "all_systems_operational"
    assert r["operational"] == 2

def test_partial_outage():
    r = generate_status_page([
        {"name": "API", "status": "operational", "group": "Core"},
        {"name": "DB", "status": "outage", "group": "Core"},
        {"name": "Web", "status": "operational", "group": "Web"},
    ])
    assert r["overall"] == "partial_outage"

def test_uptime_bars():
    r = uptime_bars([
        {"date": "2026-10-01", "uptime_pct": 100},
        {"date": "2026-10-02", "uptime_pct": 99.5},
        {"date": "2026-10-03", "uptime_pct": 98},
    ])
    assert r[0]["color"] == "green"
    assert r[2]["color"] == "red"
