"""Tests for App Changelog Timeline — events, filtering, ordering."""

import pytest

from app.services.app_changelog_timeline import AppChangelogTimeline, TimelineEventType


class TestAddEvent:
    def test_add(self):
        t = AppChangelogTimeline()
        e = t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "v2.0 Released", now=1000.0)
        assert e.event_type == TimelineEventType.RELEASE
        assert t.event_count("inst-1") == 1

    def test_missing_title(self):
        t = AppChangelogTimeline()
        with pytest.raises(ValueError, match="title"):
            t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "")


class TestTimeline:
    def test_newest_first(self):
        t = AppChangelogTimeline()
        t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "Old", now=1000.0)
        t.add_event("inst-1", "e2", TimelineEventType.INCIDENT, "New", now=2000.0)
        tl = t.get_timeline("inst-1")
        assert tl[0].event_id == "e2"

    def test_filter_by_type(self):
        t = AppChangelogTimeline()
        t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "Release")
        t.add_event("inst-1", "e2", TimelineEventType.INCIDENT, "Incident")
        tl = t.get_timeline("inst-1", event_type=TimelineEventType.RELEASE)
        assert len(tl) == 1

    def test_filter_by_time(self):
        t = AppChangelogTimeline()
        t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "A", now=1000.0)
        t.add_event("inst-1", "e2", TimelineEventType.RELEASE, "B", now=2000.0)
        t.add_event("inst-1", "e3", TimelineEventType.RELEASE, "C", now=3000.0)
        tl = t.get_timeline("inst-1", since=1500.0, until=2500.0)
        assert len(tl) == 1

    def test_limit(self):
        t = AppChangelogTimeline()
        for i in range(10):
            t.add_event("inst-1", f"e{i}", TimelineEventType.RELEASE, f"R{i}")
        tl = t.get_timeline("inst-1", limit=3)
        assert len(tl) == 3


class TestCountByType:
    def test_counts(self):
        t = AppChangelogTimeline()
        t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "A")
        t.add_event("inst-1", "e2", TimelineEventType.RELEASE, "B")
        t.add_event("inst-1", "e3", TimelineEventType.INCIDENT, "C")
        counts = t.count_by_type("inst-1")
        assert counts["release"] == 2
        assert counts["incident"] == 1


class TestIsolation:
    def test_cross_installation(self):
        t = AppChangelogTimeline()
        t.add_event("inst-1", "e1", TimelineEventType.RELEASE, "A")
        assert t.event_count("inst-2") == 0
