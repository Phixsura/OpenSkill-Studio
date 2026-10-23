from app.services.app_marketplace_app_app_app_app_app_app_app_status_page_builder import build_status_page

def test_operational():
    r = build_status_page(title="OpenSkill Status", components=[
        {"name": "API", "status": "operational", "uptime_pct": 99.99},
        {"name": "Dashboard", "status": "operational", "uptime_pct": 99.95},
    ])
    assert r["overall"] == "operational"
    assert r["all_operational"]
    assert r["component_count"] == 2

def test_degraded():
    r = build_status_page(title="Status", components=[
        {"name": "API", "status": "operational"},
        {"name": "DB", "status": "degraded"},
    ], incidents=[
        {"title": "DB slow", "status": "identified", "impact": "minor"},
    ])
    assert r["overall"] == "degraded"
    assert not r["all_operational"]
    assert r["incident_count"] == 1
