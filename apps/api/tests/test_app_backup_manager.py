"""Tests for App Backup Manager — create, complete, restore, retention."""

import pytest

from app.services.app_backup_manager import AppBackupManager, BackupStatus


class TestCreate:
    def test_create(self):
        m = AppBackupManager()
        b = m.create_backup("inst-1", "b1", label="Daily backup")
        assert b.status == BackupStatus.PENDING

    def test_duplicate(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        with pytest.raises(ValueError):
            m.create_backup("inst-1", "b1")


class TestLifecycle:
    def test_complete(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        b = m.complete_backup("inst-1", "b1", size_mb=150)
        assert b.status == BackupStatus.COMPLETED
        assert b.size_mb == 150

    def test_fail(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        b = m.fail_backup("inst-1", "b1", error="disk full")
        assert b.status == BackupStatus.FAILED

    def test_restore(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        m.complete_backup("inst-1", "b1", 100)
        b = m.restore_backup("inst-1", "b1")
        assert b.status == BackupStatus.RESTORED

    def test_cannot_restore_pending(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        with pytest.raises(ValueError):
            m.restore_backup("inst-1", "b1")


class TestRetention:
    def test_max_retention(self):
        m = AppBackupManager(max_backups=3)
        for i in range(5):
            m.create_backup("inst-1", f"b{i}")
        assert len(m.list_backups("inst-1")) == 3


class TestSize:
    def test_total_size(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        m.complete_backup("inst-1", "b1", 100)
        m.create_backup("inst-1", "b2")
        m.complete_backup("inst-1", "b2", 200)
        assert m.total_size_mb("inst-1") == 300


class TestIsolation:
    def test_cross_installation(self):
        m = AppBackupManager()
        m.create_backup("inst-1", "b1")
        with pytest.raises(KeyError):
            m._get("inst-2", "b1")
