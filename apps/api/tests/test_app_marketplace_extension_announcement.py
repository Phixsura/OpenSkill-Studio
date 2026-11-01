from app.services.app_marketplace_extension_announcement import (
    ExtensionAnnouncementService, AnnouncementType,
)


def test_create_and_get():
    svc = ExtensionAnnouncementService()
    svc.create("New Feature!", "Dark mode is here", AnnouncementType.FEATURE)
    active = svc.get_active("user-1")
    assert len(active) == 1
    assert active[0].title == "New Feature!"


def test_dismiss():
    svc = ExtensionAnnouncementService()
    ann = svc.create("Notice", "Update available")
    svc.dismiss("user-1", ann.announcement_id)
    assert len(svc.get_active("user-1")) == 0
    assert len(svc.get_active("user-2")) == 1  # other users still see it


def test_non_dismissible():
    svc = ExtensionAnnouncementService()
    ann = svc.create("Critical", "Must read", dismissible=False)
    assert svc.dismiss("user-1", ann.announcement_id) is False


def test_audience_targeting():
    svc = ExtensionAnnouncementService()
    svc.create("Dev only", "API change", target="developers")
    svc.create("All users", "General update")
    dev_anns = svc.get_active("user-1", audience="developers")
    assert len(dev_anns) == 2
    admin_anns = svc.get_active("user-2", audience="admins")
    assert len(admin_anns) == 1  # only "all" target


def test_expiry():
    svc = ExtensionAnnouncementService()
    svc.create("Expired", "Old", expires_in=-1)
    assert len(svc.get_active("user-1")) == 0


def test_deactivate():
    svc = ExtensionAnnouncementService()
    ann = svc.create("Temp", "msg")
    svc.deactivate(ann.announcement_id)
    assert len(svc.get_active("user-1")) == 0
