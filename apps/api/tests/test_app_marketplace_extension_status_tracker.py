from app.services.app_marketplace_extension_status_tracker import ExtensionStatusTrackerService

def test_set_and_get():
    svc = ExtensionStatusTrackerService()
    svc.set_status("ext-1", "active")
    assert svc.get_status("ext-1") == "active"

def test_by_status():
    svc = ExtensionStatusTrackerService()
    svc.set_status("ext-1", "active")
    svc.set_status("ext-2", "suspended")
    svc.set_status("ext-3", "active")
    assert len(svc.get_by_status("active")) == 2

def test_counts():
    svc = ExtensionStatusTrackerService()
    svc.set_status("a", "active")
    svc.set_status("b", "active")
    svc.set_status("c", "review")
    counts = svc.get_counts()
    assert counts["active"] == 2
