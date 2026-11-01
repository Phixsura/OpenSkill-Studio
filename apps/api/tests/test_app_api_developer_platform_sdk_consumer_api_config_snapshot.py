"""Tests for Consumer API Config Snapshot service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_config_snapshot import ConfigSnapshotManager


class TestConfigSnapshotManager:
    def test_set_and_snapshot(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"rate_limit": 100, "timeout": 30})
        result = svc.take_snapshot("c1", "snap-1", "Initial config")
        assert result["keys"] == 2

    def test_rollback(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"rate_limit": 100})
        svc.take_snapshot("c1", "snap-1")
        svc.set_config("c1", {"rate_limit": 200, "new_key": "val"})
        svc.rollback("c1", "snap-1")
        current = svc.get_current("c1")
        assert current["config"]["rate_limit"] == 100
        assert "new_key" not in current["config"]

    def test_diff(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"a": 1, "b": 2})
        svc.take_snapshot("c1", "s1")
        svc.set_config("c1", {"a": 1, "c": 3})
        svc.take_snapshot("c1", "s2")
        diff = svc.diff("c1", "s1", "s2")
        assert "c" in diff["added"]
        assert "b" in diff["removed"]
        assert diff["total_changes"] == 2

    def test_changed_values(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"x": 1})
        svc.take_snapshot("c1", "s1")
        svc.set_config("c1", {"x": 2})
        svc.take_snapshot("c1", "s2")
        diff = svc.diff("c1", "s1", "s2")
        assert "x" in diff["changed"]

    def test_list_snapshots(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"a": 1})
        svc.take_snapshot("c1", "s1", "First")
        svc.take_snapshot("c1", "s2", "Second")
        snaps = svc.list_snapshots("c1")
        assert len(snaps) == 2
        assert snaps[0]["label"] == "First"

    def test_delete_snapshot(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"a": 1})
        svc.take_snapshot("c1", "s1")
        assert svc.delete_snapshot("c1", "s1")["deleted"] is True
        assert svc.list_snapshots("c1") == []

    def test_no_config(self):
        svc = ConfigSnapshotManager()
        with pytest.raises(ValueError):
            svc.take_snapshot("c1", "s1")

    def test_duplicate_snapshot(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"a": 1})
        svc.take_snapshot("c1", "s1")
        with pytest.raises(ValueError):
            svc.take_snapshot("c1", "s1")

    def test_stats(self):
        svc = ConfigSnapshotManager()
        svc.set_config("c1", {"a": 1})
        svc.take_snapshot("c1", "s1")
        stats = svc.get_stats()
        assert stats["consumers_with_config"] == 1
        assert stats["total_snapshots"] == 1

    def test_isolation(self):
        a, b = ConfigSnapshotManager(), ConfigSnapshotManager()
        a.set_config("c1", {"x": 1})
        assert b.get_current("c1")["config"] == {}
