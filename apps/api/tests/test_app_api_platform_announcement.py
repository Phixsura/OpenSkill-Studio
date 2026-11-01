import pytest
from app.services.app_api_platform_announcement import AppAPIPlatformAnnouncement

class TestAnnouncement:
    def test_create(self):
        a = AppAPIPlatformAnnouncement()
        ann = a.create("inst-1", "a1", "Maintenance", "Scheduled downtime", "warning")
        assert ann.active is True

    def test_dismiss(self):
        a = AppAPIPlatformAnnouncement()
        a.create("inst-1", "a1", "Info", "Body")
        a.dismiss("inst-1", "a1")
        assert a.active_announcements("inst-1") == []

    def test_invalid_severity(self):
        a = AppAPIPlatformAnnouncement()
        with pytest.raises(ValueError):
            a.create("inst-1", "a1", "T", "B", "extreme")

    def test_isolation(self):
        a = AppAPIPlatformAnnouncement()
        a.create("inst-1", "a1", "T", "B")
        assert a.list_all("inst-2") == []
