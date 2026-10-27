"""Tests for App Version Migrator — planning, execution, rollback, pinning, consent gates."""

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
        assert plan.requires_reauth is True
        assert plan.auto_migratable is True

    def test_breaking_upgrade(self):
        m = _setup()
        plan = m.plan_upgrade("inst-1", "2.0.0")
        assert plan.compat_level == CompatLevel.BREAKING
        assert plan.auto_migratable is False

    def test_same_version_compatible(self):
        m = _setup()
        plan = m.plan_upgrade("inst-1", "1.0.0")
        assert plan.compat_level == CompatLevel.COMPATIBLE

    def test_unknown_installation_raises(self):
        m = _setup()
        with pytest.raises(ValueError, match="not found"):
            m.plan_upgrade("nonexistent", "1.1.0")

    def test_unknown_version_raises(self):
        m = _setup()
        with pytest.raises(ValueError, match="not found"):
            m.plan_upgrade("inst-1", "9.9.9")


class TestConsentGates:
    def test_requires_consent_for_new_permissions(self):
        m = _setup()
        with pytest.raises(PermissionError, match="admin consent"):
            m.start_migration("inst-1", "1.1.0")  # no consent_granted

    def test_consent_granted_allows_migration(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions={"write:submissions"})
        assert record.status == MigrationStatus.IN_PROGRESS

    def test_breaking_requires_force(self):
        m = _setup()
        with pytest.raises(ValueError, match="manual approval"):
            m.start_migration("inst-1", "2.0.0", consent_granted=True, force=False)

    def test_breaking_with_force_proceeds(self):
        m = _setup()
        record = m.start_migration("inst-1", "2.0.0", consent_granted=True, force=True)
        assert record.status == MigrationStatus.IN_PROGRESS

    def test_no_consent_needed_for_compatible(self):
        m = _setup()
        # same version: no new permissions, no breaking
        record = m.start_migration("inst-1", "1.0.0")
        assert record.status == MigrationStatus.IN_PROGRESS


class TestMigrationExecution:
    def test_start_and_complete(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions={"write:submissions"})
        assert record.config_snapshot == {"api_url": "https://lms.example.com", "timeout": "30"}
        assert sorted(record.permissions_snapshot) == ["read:projects", "read:skills"]

        completed = m.complete_migration(record.migration_id)
        assert completed.status == MigrationStatus.COMPLETED

        state = m.get_installation("inst-1")
        assert state.current_version == "1.1.0"
        assert "write:submissions" in state.granted_permissions

    def test_only_approved_permissions_added(self):
        m = _setup()
        # Plan adds write:submissions but we don't approve it
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions=set())  # no approvals
        m.complete_migration(record.migration_id)
        state = m.get_installation("inst-1")
        # write:submissions should NOT be added since it wasn't approved
        assert "write:submissions" not in state.granted_permissions

    def test_complete_requires_in_progress(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.0.0")
        m.complete_migration(record.migration_id)
        with pytest.raises(ValueError, match="Cannot complete"):
            m.complete_migration(record.migration_id)  # already completed

    def test_fail_migration(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions={"write:submissions"})
        failed = m.fail_migration(record.migration_id, "Connection timeout")
        assert failed.status == MigrationStatus.FAILED

    def test_pinned_prevents_migration(self):
        m = _setup()
        m.pin_version("inst-1")
        with pytest.raises(ValueError, match="pinned"):
            m.start_migration("inst-1", "1.1.0", consent_granted=True)

    def test_unpin_allows_migration(self):
        m = _setup()
        m.pin_version("inst-1")
        m.unpin_version("inst-1")
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions={"write:submissions"})
        assert record.status == MigrationStatus.IN_PROGRESS


class TestRollback:
    def test_rollback_restores_version_config_and_permissions(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions={"write:submissions"})
        m.complete_migration(record.migration_id)

        state = m.get_installation("inst-1")
        assert state.current_version == "1.1.0"
        assert "write:submissions" in state.granted_permissions

        m.rollback(record.migration_id)
        state = m.get_installation("inst-1")
        assert state.current_version == "1.0.0"
        assert state.config == {"api_url": "https://lms.example.com", "timeout": "30"}
        # Permissions restored to pre-migration snapshot
        assert "write:submissions" not in state.granted_permissions
        assert "read:projects" in state.granted_permissions

    def test_rollback_failed(self):
        m = _setup()
        record = m.start_migration("inst-1", "2.0.0", consent_granted=True, force=True)
        m.fail_migration(record.migration_id, "error")
        rolled = m.rollback(record.migration_id)
        assert rolled.status == MigrationStatus.ROLLED_BACK

    def test_rollback_in_progress_raises(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                    approved_permissions={"write:submissions"})
        with pytest.raises(ValueError, match="Cannot rollback"):
            m.rollback(record.migration_id)

    def test_rollback_unknown_raises(self):
        m = _setup()
        with pytest.raises(ValueError, match="not found"):
            m.rollback("nonexistent")


class TestHistory:
    def test_get_history(self):
        m = _setup()
        r1 = m.start_migration("inst-1", "1.1.0", consent_granted=True,
                                approved_permissions={"write:submissions"})
        m.complete_migration(r1.migration_id)
        r2 = m.start_migration("inst-1", "2.0.0", consent_granted=True, force=True)
        m.complete_migration(r2.migration_id)
        history = m.get_history("inst-1")
        assert len(history) == 2
        assert history[0].to_version == "2.0.0"

    def test_empty_history(self):
        m = _setup()
        assert m.get_history("inst-1") == []

    def test_get_migration(self):
        m = _setup()
        record = m.start_migration("inst-1", "1.0.0")
        fetched = m.get_migration(record.migration_id)
        assert fetched is not None

    def test_get_migration_unknown(self):
        m = _setup()
        assert m.get_migration("nonexistent") is None
