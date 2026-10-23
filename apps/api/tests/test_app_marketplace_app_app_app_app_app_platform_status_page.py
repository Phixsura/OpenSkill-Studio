from app.services.app_marketplace_app_app_app_app_app_platform_status_page import build_platform_status_page

def test_all_operational():
    statuses = {s: "operational" for s in ["api", "web", "auth", "db", "cache", "storage", "webhooks", "analytics", "search", "cdn"]}
    r = build_platform_status_page(statuses=statuses)
    assert r["overall"] == "operational"
    assert r["healthy"] == 10
    assert r["overall_label"] == "All Systems Operational"

def test_degraded():
    statuses = {"api": "operational", "db": "degraded"}
    r = build_platform_status_page(statuses=statuses)
    assert r["overall"] == "degraded"

def test_incidents():
    r = build_platform_status_page(statuses={}, incidents=[{"title": "DB slow", "status": "investigating"}])
    assert len(r["incidents"]) == 1
