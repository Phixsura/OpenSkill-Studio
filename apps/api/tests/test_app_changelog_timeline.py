"""Tests for App Changelog Timeline — milestones, query, filter."""

import pytest

from app.services.app_changelog_timeline import AppChangelogTimeline


class TestAdd:
    def test_add(self):
        t = AppChangelogTimeline()
        ms = t.add_milestone("inst-1", "m1", "v2.0 Release", "release", "v2.0")
        assert ms.milestone_type == "release"

    def test_invalid_type(self):
        t = AppChangelogTimeline()
        with pytest.raises(ValueError):
            t.add_milestone("inst-1", "m1", "Bad", "bogus")


class TestQuery:
    def test_recent(self):
        t = AppChangelogTimeline()
        for i in range(5):
            t.add_milestone("inst-1", f"m{i}", f"Title {i}", "feature")
        recent = t.recent("inst-1", limit=3)
        assert len(recent) == 3
        assert recent[0].milestone_id == "m4"

    def test_by_type(self):
        t = AppChangelogTimeline()
        t.add_milestone("inst-1", "m1", "Release", "release")
        t.add_milestone("inst-1", "m2", "Fix", "fix")
        assert len(t.by_type("inst-1", "release")) == 1


class TestIsolation:
    def test_cross(self):
        t = AppChangelogTimeline()
        t.add_milestone("inst-1", "m1", "Title", "feature")
        assert t.count("inst-2") == 0
