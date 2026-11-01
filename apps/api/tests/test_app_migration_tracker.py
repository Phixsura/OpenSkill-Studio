"""Tests for App Migration Tracker — lifecycle, dependencies, rollback."""

import pytest

from app.services.app_migration_tracker import AppMigrationTracker, MigrationStatus


class TestRegister:
    def test_register(self):
        t = AppMigrationTracker()
        m = t.register("inst-1", "m1", "001", "Create users table")
        assert m.status == MigrationStatus.PENDING

    def test_duplicate(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "Create users")
        with pytest.raises(ValueError, match="already registered"):
            t.register("inst-1", "m1", "001", "Duplicate")


class TestLifecycle:
    def test_start_complete(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "Create users")
        t.start("inst-1", "m1")
        m = t.complete("inst-1", "m1")
        assert m.status == MigrationStatus.COMPLETED
        assert m.duration_ms is not None

    def test_fail(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "Add index")
        t.start("inst-1", "m1")
        m = t.fail("inst-1", "m1", "timeout")
        assert m.status == MigrationStatus.FAILED
        assert m.error == "timeout"


class TestDependency:
    def test_blocked_by_dependency(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "Create table")
        t.register("inst-1", "m2", "002", "Add column", depends_on="m1")
        with pytest.raises(ValueError, match="not completed"):
            t.start("inst-1", "m2")

    def test_dependency_satisfied(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "Create table")
        t.register("inst-1", "m2", "002", "Add column", depends_on="m1")
        t.start("inst-1", "m1")
        t.complete("inst-1", "m1")
        m = t.start("inst-1", "m2")
        assert m.status == MigrationStatus.RUNNING


class TestRollback:
    def test_rollback_completed(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "X")
        t.start("inst-1", "m1")
        t.complete("inst-1", "m1")
        m = t.rollback("inst-1", "m1")
        assert m.status == MigrationStatus.ROLLED_BACK


class TestIsolation:
    def test_cross(self):
        t = AppMigrationTracker()
        t.register("inst-1", "m1", "001", "X")
        assert t.list_all("inst-2") == []
