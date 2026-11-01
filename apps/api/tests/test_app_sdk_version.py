"""Tests for App SDK Version — record, outdated, stats."""

import pytest

from app.services.app_sdk_version import AppSDKVersion


class TestRecord:
    def test_record(self):
        s = AppSDKVersion()
        info = s.record_usage("inst-1", "1.2.0", "consumer-a")
        assert info.request_count == 1
        assert info.consumer_count == 1

    def test_unique_consumers(self):
        s = AppSDKVersion()
        s.record_usage("inst-1", "1.2.0", "a")
        s.record_usage("inst-1", "1.2.0", "a")
        s.record_usage("inst-1", "1.2.0", "b")
        info = s.record_usage("inst-1", "1.2.0", "b")
        assert info.request_count == 4
        assert info.consumer_count == 2


class TestOutdated:
    def test_outdated(self):
        s = AppSDKVersion()
        s.set_latest("inst-1", "2.0.0")
        s.record_usage("inst-1", "1.0.0", "old-app")
        s.record_usage("inst-1", "2.0.0", "new-app")
        outdated = s.outdated_consumers("inst-1")
        assert len(outdated) == 1
        assert outdated[0]["consumer"] == "old-app"


class TestStats:
    def test_stats(self):
        s = AppSDKVersion()
        s.set_latest("inst-1", "2.0.0")
        s.record_usage("inst-1", "1.0.0", "a")
        s.record_usage("inst-1", "2.0.0", "b")
        stats = s.version_stats("inst-1")
        assert len(stats) == 2
        latest = [x for x in stats if x["latest"]]
        assert len(latest) == 1


class TestIsolation:
    def test_cross(self):
        s = AppSDKVersion()
        s.record_usage("inst-1", "1.0.0", "a")
        assert s.version_stats("inst-2") == []
