"""Tests for App Version Migrator — planning, execution, rollback, pinning."""

import pytest

from app.services.app_version_migrator import (
    AppVersionMigrator,
    CompatLevel,
    InstallationState,
    MigrationStatus,
    VersionInfo,
)


def _setup() -> AppVersionMigrator:
    m = AppVersionMigrator()
    m.register_version("app-1", VersionInfo(
        version="1.0.0",
        permissions=["read:skills", "read:projects"],
        config_schema={"api_url": "url", "timeout": "integer"},
    ))
    m.register_version("app-1", VersionInfo(
        version="1.1.0",
        permissions=["read:skills", "read:projects", "write:submissions"],
        config_schema={"api_url": "url", "timeout": "integer", "batch_size": "integer"},
    ))
    m.register_version("app-1", VersionInfo(
        version="2.0.0",
        permissions=["read:skills", "write:submissions"],  # removed read:projects
        config_schema={"api_url": "url", "batch_size": "integer"},  # removed timeout
    ))
    m.register_installation(InstallationState(
        installation_id="inst-1", app_id="app-1", current_version="1.0.0",
        config={"api_url": "https://lms.example.com", "timeout": "30"},
        granted_permissions=["read:skills", "read:projects"],
    ))
    return m


class TestPlanUpgrade:
    def test_compatible_upgrade(self):
        m = _setup()
        plan = m.plan_upgrade("inst-1", "1.1.0")
        assert plan.compat_level == CompatLevel.MINOR_CHANGES
        assert "write:submissions" in plan.added_permissions
        assert "batch_size" in plan.added_config
        assert plan.removed_permissions == []
        assert plan.removed_config == []
        assert plan.requires_reauth is True
        assert plan.auto_migratable is True

    def test_breaking_upgrade(self):
        m = _setup()
        plan = m.plan_upgrade("inst-1", "2.0.0")
        assert plan.compat_level == CompatLevel.BREAKING
        assert "read:projects" in plan.removed_permissions
        assert "timeout" in plan.removed_config
        assert plan.auto_migratable is False
        assert len(plan.breaking_reasons) > 0

    def test_same_version_compatible(self):
        m = _setup()
        plan = m.plan_upgrade("inst-1", "1.0.0")
        assert plan.compat_level == CompatLevel.COMPATIBLE
        assert plan.added_permissions == []
        assert plan.removed_permissions == []

    def test_unknown_installation_raises(self):
        m = _setup()
        with pytest.raises(ValueError, match="not found"):
            m.plan_upgrade("nonexistent", "1.1.0")

    def test_unknown_version_raises(self):
        m = _setup()
        with pytest.raises(ValueError, match="not found"):
            m.plan_upgrade("inst-1", "9.9.9")


class TestMigrationExecution:
    def test_start_and_complete(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0")
        assert record.status == MigrationStatus.IN_PROGRESS
        assert record.from_version == "1.0.0"
        assert record.to_version == "1.1.0"
        assert record.config_snapshot == {"api_url": "https://lms.example.com", "timeout": "30"}

        completed = m.complete_migration(record.migration_id)
        assert completed.status == MigrationStatus.COMPLETED
        assert completed.completed_at is not None

        state = m.get_installation("inst-1")
        assert state.current_version == "1.1.0"
        assert "write:submissions" in state.granted_permissions

    def test_fail_migration(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0")
        failed = m.fail_migration(record.migration_id, "Connection timeout")
        assert failed.status == MigrationStatus.FAILED
        assert failed.error == "Connection timeout"

    def test_pinned_prevents_migration(self):
        m = _setup()
        m.pin_version("inst-1")
        with pytest.raises(ValueError, match="pinned"):
            m.start_migration("inst-1", "1.1.0")

    def test_unpin_allows_migration(self):
        m = _setup()
        m.pin_version("inst-1")
        m.unpin_version("inst-1")
        record = m.start_migration("inst-1", "1.1.0")
        assert record.status == MigrationStatus.IN_PROGRESS


class TestRollback:
    def test_rollback_completed(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0")
        m.complete_migration(record.migration_id)

        state = m.get_installation("inst-1")
        assert state.current_version == "1.1.0"

        rolled = m.rollback(record.migration_id)
        assert rolled.status == MigrationStatus.ROLLED_BACK

        state = m.get_installation("inst-1")
        assert state.current_version == "1.0.0"
        assert state.config == {"api_url": "https://lms.example.com", "timeout": "30"}

    def test_rollback_failed(self):
        m = _setup()
        record = m.start_migration("inst-1", "2.0.0")
        m.fail_migration(record.migration_id, "error")
        rolled = m.rollback(record.migration_id)
        assert rolled.status == MigrationStatus.ROLLED_BACK

    def test_rollback_in_progress_raises(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0")
        with pytest.raises(ValueError, match="Cannot rollback"):
            m.rollback(record.migration_id)

    def test_rollback_unknown_raises(self):
        m = _setup()
        with pytest.raises(ValueError, match="not found"):
            m.rollback("nonexistent")


class TestHistory:
    def test_get_history(self):
        m = _setup()
        r1 = m.start_migration("inst-1", "1.1.0")
        m.complete_migration(r1.migration_id)
        r2 = m.start_migration("inst-1", "2.0.0")
        m.complete_migration(r2.migration_id)
        history = m.get_history("inst-1")
        assert len(history) == 2
        assert history[0].to_version == "2.0.0"  # most recent first

    def test_empty_history(self):
        m = _setup()
        assert m.get_history("inst-1") == []

    def test_get_migration(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0")
        fetched = m.get_migration(record.migration_id)
        assert fetched is not None
        assert fetched.migration_id == record.migration_id

    def test_get_migration_unknown(self):
        m = _setup()
        assert m.get_migration("nonexistent") is None


class TestPermissionUpdates:
    def test_added_permissions_after_upgrade(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0")
        m.complete_migration(record.migration_id)
        state = m.get_installation("inst-1")
        assert "write:submissions" in state.granted_permissions
        assert "read:skills" in state.granted_permissions

    def test_removed_permissions_after_breaking_upgrade(self):
        m = _setup()
        # First upgrade to 1.1.0
        r1 = m.start_migration("inst-1", "1.1.0")
        m.complete_migration(r1.migration_id)
        # Then to 2.0.0 (removes read:projects)
        r2 = m.start_migration("inst-1", "2.0.0")
        m.complete_migration(r2.migration_id)
        state = m.get_installation("inst-1")
        assert "read:projects" not in state.granted_permissions
        assert "write:submissions" in state.granted_permissions
