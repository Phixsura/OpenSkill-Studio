from app.services.app_marketplace_extension_change_history import ExtensionChangeHistoryService


def test_record_and_get():
    svc = ExtensionChangeHistoryService()
    svc.record("ext-1", "deploy", "Deployed v2.0", "admin",
               diff={"version": {"from": "1.0", "to": "2.0"}})
    history = svc.get_history("ext-1")
    assert len(history) == 1
    assert history[0].description == "Deployed v2.0"


def test_filter_by_type():
    svc = ExtensionChangeHistoryService()
    svc.record("ext-1", "config", "Changed theme", "alice")
    svc.record("ext-1", "deploy", "Deployed", "bob")
    svc.record("ext-1", "config", "Changed port", "alice")
    assert len(svc.get_history("ext-1", change_type="config")) == 2


def test_filter_by_actor():
    svc = ExtensionChangeHistoryService()
    svc.record("ext-1", "deploy", "v1", "alice")
    svc.record("ext-1", "deploy", "v2", "bob")
    assert len(svc.get_history("ext-1", actor="alice")) == 1


def test_get_types():
    svc = ExtensionChangeHistoryService()
    svc.record("ext-1", "deploy", "d1", "x")
    svc.record("ext-1", "deploy", "d2", "x")
    svc.record("ext-1", "config", "c1", "x")
    types = svc.get_types("ext-1")
    assert types["deploy"] == 2
    assert types["config"] == 1


def test_get_actors():
    svc = ExtensionChangeHistoryService()
    svc.record("ext-1", "deploy", "d", "alice")
    svc.record("ext-1", "config", "c", "bob")
    assert svc.get_actors("ext-1") == ["alice", "bob"]
