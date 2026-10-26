from app.services.app_marketplace_extension_sandbox_migration_runner import (
    SandboxMigrationRunnerService, MigrationState,
)
import pytest


def test_register():
    svc = SandboxMigrationRunnerService()
    m = svc.register("sb-1", "001", "add_users_table", "CREATE TABLE users", "DROP TABLE users")
    assert m.state == MigrationState.PENDING


def test_migrate_up():
    svc = SandboxMigrationRunnerService()
    svc.register("sb-1", "001", "create_users", "up1", "down1")
    svc.register("sb-1", "002", "add_email", "up2", "down2")
    applied = svc.migrate_up("sb-1")
    assert len(applied) == 2
    assert all(m.state == MigrationState.APPLIED for m in applied)


def test_migrate_up_to():
    svc = SandboxMigrationRunnerService()
    svc.register("sb-1", "001", "a", "up", "down")
    svc.register("sb-1", "002", "b", "up", "down")
    svc.register("sb-1", "003", "c", "up", "down")
    applied = svc.migrate_up_to("sb-1", "002")
    assert len(applied) == 2
    status = svc.get_status("sb-1")
    assert status["pending"] == 1


def test_rollback_last():
    svc = SandboxMigrationRunnerService()
    svc.register("sb-1", "001", "a", "up", "down")
    svc.register("sb-1", "002", "b", "up", "down")
    svc.migrate_up("sb-1")
    rolled = svc.rollback_last("sb-1")
    assert rolled.version == "002"
    assert rolled.state == MigrationState.ROLLED_BACK


def test_rollback_to():
    svc = SandboxMigrationRunnerService()
    for i in range(1, 6):
        svc.register("sb-1", f"00{i}", f"m{i}", "up", "down")
    svc.migrate_up("sb-1")
    rolled = svc.rollback_to("sb-1", "002")
    assert len(rolled) == 3  # 003, 004, 005
    status = svc.get_status("sb-1")
    assert status["current_version"] == "002"


def test_duplicate_version_rejected():
    svc = SandboxMigrationRunnerService()
    svc.register("sb-1", "001", "a", "up", "down")
    with pytest.raises(ValueError, match="already registered"):
        svc.register("sb-1", "001", "b", "up", "down")


def test_fail_migration():
    svc = SandboxMigrationRunnerService()
    svc.register("sb-1", "001", "a", "up", "down")
    svc.fail_migration("sb-1", "001", "syntax error")
    status = svc.get_status("sb-1")
    assert status["failed"] == 1


def test_status():
    svc = SandboxMigrationRunnerService()
    svc.register("sb-1", "001", "a", "up", "down")
    svc.register("sb-1", "002", "b", "up", "down")
    svc.migrate_up_to("sb-1", "001")
    status = svc.get_status("sb-1")
    assert status["applied"] == 1
    assert status["pending"] == 1
    assert status["current_version"] == "001"
