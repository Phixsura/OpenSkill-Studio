from app.services.app_marketplace_extension_rollback import (
    ExtensionRollbackService, RollbackStatus,
)


def test_register_versions():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    svc.register_version("ext-1", "2.0.0")
    assert svc.get_current_version("ext-1") == "2.0.0"
    assert len(svc.get_available_versions("ext-1")) == 2


def test_rollback():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    svc.register_version("ext-1", "2.0.0")
    record = svc.rollback("ext-1", "1.0.0", "Bug in v2", "admin")
    assert record.status == RollbackStatus.COMPLETED
    assert svc.get_current_version("ext-1") == "1.0.0"


def test_cannot_rollback_same():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    result = svc.rollback("ext-1", "1.0.0", "test", "admin")
    assert "error" in result


def test_cannot_rollback_missing():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    result = svc.rollback("ext-1", "9.9.9", "test", "admin")
    assert "error" in result


def test_rollforward():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    svc.register_version("ext-1", "2.0.0")
    record = svc.rollback("ext-1", "1.0.0", "test", "admin")
    assert svc.rollforward(record.rollback_id) is True
    assert svc.get_current_version("ext-1") == "2.0.0"
    assert record.status == RollbackStatus.ROLLED_FORWARD


def test_history():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    svc.register_version("ext-1", "2.0.0")
    svc.rollback("ext-1", "1.0.0", "bug", "admin")
    history = svc.get_history("ext-1")
    assert len(history) == 1
    assert history[0].reason == "bug"


def test_can_rollback_check():
    svc = ExtensionRollbackService()
    svc.register_version("ext-1", "1.0.0")
    svc.register_version("ext-1", "2.0.0")
    assert svc.can_rollback("ext-1", "1.0.0")["can_rollback"] is True
    assert svc.can_rollback("ext-1", "2.0.0")["can_rollback"] is False  # current
