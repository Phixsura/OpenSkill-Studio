from app.services.app_marketplace_extension_status_page import ExtStatusPageService

def test_create():
    svc = ExtStatusPageService()
    page = svc.create("ext-1", "Auth Service Status", ["API", "Auth", "Database"])
    assert len(page.services) == 3
    assert page.overall == "operational"

def test_update_service():
    svc = ExtStatusPageService()
    svc.create("ext-1", "Status", ["API", "DB"])
    svc.update_service("ext-1", "DB", "degraded", 98.5)
    page = svc.get("ext-1")
    assert page.overall == "degraded"

def test_worst_status_wins():
    svc = ExtStatusPageService()
    svc.create("ext-1", "Status", ["API", "DB", "Cache"])
    svc.update_service("ext-1", "API", "operational")
    svc.update_service("ext-1", "DB", "major_outage", 85.0)
    svc.update_service("ext-1", "Cache", "degraded", 95.0)
    assert svc.get("ext-1").overall == "major_outage"

def test_uptime_summary():
    svc = ExtStatusPageService()
    svc.create("ext-1", "Status", ["API", "DB"])
    svc.update_service("ext-1", "API", "operational", 99.9)
    svc.update_service("ext-1", "DB", "operational", 99.5)
    summary = svc.get_uptime_summary("ext-1")
    assert summary["avg_uptime"] == 99.7
