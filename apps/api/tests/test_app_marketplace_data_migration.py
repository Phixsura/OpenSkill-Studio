from app.services.app_marketplace_data_migration import (
    DataMigrationService, Migration, MigrationStatus,
)


def _make_migration(mid: str, ext: str, from_v: str, to_v: str) -> Migration:
    return Migration(mid, ext, from_v, to_v, f"Migrate {from_v} to {to_v}", "up", "down")


def test_register_and_pending():
    svc = DataMigrationService()
    svc.register(_make_migration("m1", "ext-1", "1.0", "1.1"))
    svc.register(_make_migration("m2", "ext-1", "1.1", "1.2"))
    pending = svc.get_pending("ext-1")
    assert len(pending) == 2


def test_apply_migration():
    svc = DataMigrationService()
    svc.register(_make_migration("m1", "ext-1", "1.0", "1.1"))
    ok, msg = svc.apply("m1")
    assert ok is True
    assert "1.0 -> 1.1" in msg
    assert svc.get_current_version("ext-1") == "1.1"
    assert len(svc.get_pending("ext-1")) == 0


def test_rollback():
    svc = DataMigrationService()
    svc.register(_make_migration("m1", "ext-2", "1.0", "1.1"))
    svc.apply("m1")
    ok, msg = svc.rollback("m1")
    assert ok is True
    assert "1.1 -> 1.0" in msg
    assert svc.get_current_version("ext-2") == "0.0.0"


def test_cannot_rollback_non_latest():
    svc = DataMigrationService()
    svc.register(_make_migration("m1", "ext-3", "1.0", "1.1"))
    svc.register(_make_migration("m2", "ext-3", "1.1", "1.2"))
    svc.apply("m1")
    svc.apply("m2")
    ok, msg = svc.rollback("m1")  # not the latest
    assert ok is False
    assert "most recent" in msg


def test_cannot_apply_twice():
    svc = DataMigrationService()
    svc.register(_make_migration("m1", "ext-4", "1.0", "1.1"))
    svc.apply("m1")
    ok, msg = svc.apply("m1")
    assert ok is False


def test_history():
    svc = DataMigrationService()
    svc.register(_make_migration("m1", "ext-5", "1.0", "1.1"))
    svc.register(_make_migration("m2", "ext-5", "1.1", "1.2"))
    svc.apply("m1")
    svc.apply("m2")
    history = svc.get_history("ext-5")
    assert len(history) == 2
    assert history[0].from_version == "1.0"
    assert history[1].to_version == "1.2"
