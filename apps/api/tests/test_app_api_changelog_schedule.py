import pytest
from app.services.app_api_changelog_schedule import AppAPIChangelogSchedule, PublishStatus

class TestSchedule:
    def test_schedule(self):
        s = AppAPIChangelogSchedule()
        sc = s.schedule("inst-1", "s1", "v3.0", "Major Release", "2025-02-01")
        assert sc.status == PublishStatus.SCHEDULED

    def test_publish(self):
        s = AppAPIChangelogSchedule()
        s.schedule("inst-1", "s1", "v3.0", "Release", "2025-02-01")
        s.publish("inst-1", "s1")
        assert s.upcoming("inst-1") == []

    def test_cancel(self):
        s = AppAPIChangelogSchedule()
        s.schedule("inst-1", "s1", "v3.0", "Release", "2025-02-01")
        s.cancel("inst-1", "s1")
        assert s.list_all("inst-1")[0].status == PublishStatus.CANCELLED

    def test_isolation(self):
        s = AppAPIChangelogSchedule()
        s.schedule("inst-1", "s1", "v1", "A", "2025-01")
        assert s.list_all("inst-2") == []
