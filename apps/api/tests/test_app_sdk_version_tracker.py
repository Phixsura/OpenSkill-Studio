"""Tests for App SDK Version Tracker — versions, outdated, distribution."""

import pytest

from app.services.app_sdk_version_tracker import AppSDKVersionTracker


class TestRecord:
    def test_record(self):
        t = AppSDKVersionTracker(latest_version="2.0.0")
        u = t.record("inst-1", "1.5.0", "python")
        assert u.sdk_version == "1.5.0"
        assert u.language == "python"

    def test_missing_version(self):
        t = AppSDKVersionTracker()
        with pytest.raises(ValueError):
            t.record("inst-1", "")


class TestOutdated:
    def test_outdated(self):
        t = AppSDKVersionTracker(latest_version="2.0.0")
        t.record("inst-1", "1.5.0")
        assert t.is_outdated("inst-1") is True

    def test_current(self):
        t = AppSDKVersionTracker(latest_version="2.0.0")
        t.record("inst-1", "2.0.0")
        assert t.is_outdated("inst-1") is False

    def test_ahead(self):
        t = AppSDKVersionTracker(latest_version="2.0.0")
        t.record("inst-1", "2.1.0")
        assert t.is_outdated("inst-1") is False

    def test_get_outdated(self):
        t = AppSDKVersionTracker(latest_version="2.0.0")
        t.record("inst-1", "1.5.0")
        t.record("inst-2", "2.0.0")
        t.record("inst-3", "1.0.0")
        outdated = t.get_outdated()
        assert len(outdated) == 2


class TestDistribution:
    def test_version_dist(self):
        t = AppSDKVersionTracker()
        t.record("inst-1", "1.0.0")
        t.record("inst-2", "1.0.0")
        t.record("inst-3", "2.0.0")
        dist = t.version_distribution()
        assert dist["1.0.0"] == 2
        assert dist["2.0.0"] == 1

    def test_language_dist(self):
        t = AppSDKVersionTracker()
        t.record("inst-1", "1.0.0", "python")
        t.record("inst-2", "1.0.0", "typescript")
        t.record("inst-3", "1.0.0", "python")
        dist = t.language_distribution()
        assert dist["python"] == 2
        assert dist["typescript"] == 1


class TestMisc:
    def test_total(self):
        t = AppSDKVersionTracker()
        t.record("inst-1", "1.0.0")
        t.record("inst-2", "1.0.0")
        assert t.total_installations() == 2

    def test_unknown_installation(self):
        t = AppSDKVersionTracker()
        assert t.get_usage("nope") is None

    def test_set_latest(self):
        t = AppSDKVersionTracker(latest_version="1.0.0")
        t.record("inst-1", "1.0.0")
        assert t.is_outdated("inst-1") is False
        t.set_latest("2.0.0")
        assert t.is_outdated("inst-1") is True
