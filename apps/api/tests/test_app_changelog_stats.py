"""Tests for App Changelog Stats — aggregation, cadence, contributors."""

import pytest

from app.services.app_changelog_stats import AppChangelogStats, ReleaseData


def _release(version, ts, entries=3, breaking=0, cats=None, contributors=None):
    return ReleaseData(version=version, timestamp=ts, entry_count=entries,
                       breaking_count=breaking, categories=cats or {"added": entries},
                       contributors=contributors or [])


class TestCompute:
    def test_basic(self):
        s = AppChangelogStats()
        s.add_release("inst-1", _release("1.0.0", 1000))
        s.add_release("inst-1", _release("2.0.0", 2000, breaking=1))
        stats = s.compute("inst-1")
        assert stats.total_releases == 2
        assert stats.total_entries == 6
        assert stats.breaking_changes == 1

    def test_categories(self):
        s = AppChangelogStats()
        s.add_release("inst-1", _release("1.0", 1000, cats={"added": 2, "fixed": 1}))
        s.add_release("inst-1", _release("2.0", 2000, cats={"added": 1, "removed": 1}))
        stats = s.compute("inst-1")
        assert stats.categories["added"] == 3
        assert stats.categories["fixed"] == 1

    def test_contributors(self):
        s = AppChangelogStats()
        s.add_release("inst-1", _release("1.0", 1000, contributors=["alice", "bob"]))
        s.add_release("inst-1", _release("2.0", 2000, contributors=["alice"]))
        stats = s.compute("inst-1")
        assert stats.top_contributors[0] == ("alice", 2)

    def test_cadence(self):
        s = AppChangelogStats()
        s.add_release("inst-1", _release("1.0", 0))
        s.add_release("inst-1", _release("2.0", 86400 * 7))
        s.add_release("inst-1", _release("3.0", 86400 * 21))
        stats = s.compute("inst-1")
        assert stats.avg_days_between_releases == 10.5

    def test_empty(self):
        s = AppChangelogStats()
        stats = s.compute("inst-1")
        assert stats.total_releases == 0

    def test_single_release(self):
        s = AppChangelogStats()
        s.add_release("inst-1", _release("1.0", 1000))
        stats = s.compute("inst-1")
        assert stats.avg_days_between_releases == 0


class TestIsolation:
    def test_cross_installation(self):
        s = AppChangelogStats()
        s.add_release("inst-1", _release("1.0", 1000))
        stats = s.compute("inst-2")
        assert stats.total_releases == 0
