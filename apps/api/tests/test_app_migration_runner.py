"""Tests for App Migration Runner — ordering, apply, rollback, version tracking."""

import pytest

from app.services.app_migration_runner import AppMigrationRunner, MigrationStatus


class TestRegister:
    def test_register(self):
        r = AppMigrationRunner()
        m = r.register_migration("inst-1", "m1", 1, "Create users table")
        assert m.migration_id == "m1"
        assert m.version == 1
        assert m.status == MigrationStatus.PENDING

    def test_duplicate(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        with pytest.raises(ValueError, match="already registered"):
            r.register_migration("inst-1", "m1", 2, "Dup")

    def test_duplicate_version(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        with pytest.raises(ValueError, match="Version 1"):
            r.register_migration("inst-1", "m2", 1, "Same version")

    def test_invalid_version(self):
        r = AppMigrationRunner()
        with pytest.raises(ValueError, match="version"):
            r.register_migration("inst-1", "m1", 0, "Bad")


class TestApply:
    def test_apply(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Create table")
        m = r.apply_migration("inst-1", "m1", duration_ms=150.0, now=1000.0)
        assert m.status == MigrationStatus.APPLIED
        assert m.applied_at == 1000.0
        assert m.duration_ms == 150.0

    def test_apply_requires_order(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        r.register_migration("inst-1", "m2", 2, "Second")
        with pytest.raises(ValueError, match="Previous migration"):
            r.apply_migration("inst-1", "m2")

    def test_apply_in_order(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        r.register_migration("inst-1", "m2", 2, "Second")
        r.apply_migration("inst-1", "m1")
        m = r.apply_migration("inst-1", "m2")
        assert m.status == MigrationStatus.APPLIED

    def test_apply_failed_retry(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Table")
        r.fail_migration("inst-1", "m1", "timeout")
        m = r.apply_migration("inst-1", "m1")
        assert m.status == MigrationStatus.APPLIED
        assert m.error is None

    def test_cannot_apply_applied(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Table")
        r.apply_migration("inst-1", "m1")
        with pytest.raises(ValueError, match="Cannot apply"):
            r.apply_migration("inst-1", "m1")


class TestFail:
    def test_fail(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Table")
        m = r.fail_migration("inst-1", "m1", "connection error")
        assert m.status == MigrationStatus.FAILED
        assert m.error == "connection error"


class TestRollback:
    def test_rollback(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Table")
        r.apply_migration("inst-1", "m1")
        m = r.rollback_migration("inst-1", "m1")
        assert m.status == MigrationStatus.ROLLED_BACK

    def test_cannot_rollback_with_later_applied(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        r.register_migration("inst-1", "m2", 2, "Second")
        r.apply_migration("inst-1", "m1")
        r.apply_migration("inst-1", "m2")
        with pytest.raises(ValueError, match="Later migration"):
            r.rollback_migration("inst-1", "m1")

    def test_cannot_rollback_pending(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Table")
        with pytest.raises(ValueError, match="Cannot roll back"):
            r.rollback_migration("inst-1", "m1")


class TestVersion:
    def test_current_version(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        r.register_migration("inst-1", "m2", 2, "Second")
        r.apply_migration("inst-1", "m1")
        assert r.current_version("inst-1") == 1

    def test_no_applied(self):
        r = AppMigrationRunner()
        assert r.current_version("inst-1") == 0


class TestListing:
    def test_list_in_order(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m2", 2, "Second")
        r.register_migration("inst-1", "m1", 1, "First")
        migrations = r.list_migrations("inst-1")
        assert [m.version for m in migrations] == [1, 2]

    def test_get_pending(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "First")
        r.register_migration("inst-1", "m2", 2, "Second")
        r.apply_migration("inst-1", "m1")
        pending = r.get_pending("inst-1")
        assert len(pending) == 1
        assert pending[0].migration_id == "m2"


class TestIsolation:
    def test_cross_installation(self):
        r = AppMigrationRunner()
        r.register_migration("inst-1", "m1", 1, "Table")
        with pytest.raises(KeyError):
            r.get_migration("inst-2", "m1")
