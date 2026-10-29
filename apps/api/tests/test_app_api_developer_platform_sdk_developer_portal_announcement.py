import pytest, time
from app.services.app_api_developer_platform_sdk_developer_portal_announcement import AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement

class TestPortalAnnouncement:
    def test_create(self):
        a = AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement()
        ann = a.create("inst-1", "a1", "Maintenance Window", "Scheduled downtime", "maintenance")
        assert ann.severity == "maintenance"

    def test_view(self):
        a = AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement()
        a.create("inst-1", "a1", "News", "Update", "info")
        a.view("inst-1", "a1")
        assert a.all_announcements("inst-1")[0].views == 1

    def test_dismiss(self):
        a = AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement()
        a.create("inst-1", "a1", "Alert", "Fix", "warning")
        a.dismiss("inst-1", "a1")
        assert len(a.active_announcements("inst-1")) == 0

    def test_expired(self):
        a = AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement()
        ann = a.create("inst-1", "a1", "Old", "Past", "info", expires_at=time.time() - 1)
        assert len(a.active_announcements("inst-1")) == 0

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKDeveloperPortalAnnouncement()
        a.create("inst-1", "a1", "X", "Y", "info")
        assert len(a.all_announcements("inst-2")) == 0
