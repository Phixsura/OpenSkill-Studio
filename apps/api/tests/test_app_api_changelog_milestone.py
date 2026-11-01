import pytest
from app.services.app_api_changelog_milestone import AppAPIChangelogMilestone

class TestMilestone:
    def test_create(self):
        m = AppAPIChangelogMilestone()
        ms = m.create("inst-1", "m1", "GA Release", "v1.0")
        assert ms.pinned is False

    def test_pin(self):
        m = AppAPIChangelogMilestone()
        m.create("inst-1", "m1", "GA", "v1.0")
        m.pin("inst-1", "m1")
        assert len(m.pinned("inst-1")) == 1

    def test_duplicate(self):
        m = AppAPIChangelogMilestone()
        m.create("inst-1", "m1", "A", "v1")
        with pytest.raises(ValueError):
            m.create("inst-1", "m1", "B", "v2")

    def test_isolation(self):
        m = AppAPIChangelogMilestone()
        m.create("inst-1", "m1", "A", "v1")
        assert m.list_milestones("inst-2") == []
