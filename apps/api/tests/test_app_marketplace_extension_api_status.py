from app.services.app_marketplace_extension_api_status import PlatformApiStatusService

def test_set_and_get():
    svc = PlatformApiStatusService()
    svc.set_status("/api/users", "GET", "operational", 45)
    assert len(svc.get_all()) == 1

def test_overall():
    svc = PlatformApiStatusService()
    svc.set_status("/api/users", "GET", "operational")
    svc.set_status("/api/data", "POST", "degraded")
    assert svc.get_overall() == "degraded"

def test_by_status():
    svc = PlatformApiStatusService()
    svc.set_status("/a", "GET", "operational")
    svc.set_status("/b", "GET", "down")
    assert len(svc.get_by_status("down")) == 1
