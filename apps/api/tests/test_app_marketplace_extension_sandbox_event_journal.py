from app.services.app_marketplace_extension_sandbox_event_journal import (
    SandboxEventJournalService,
)


def test_append_and_sequence():
    svc = SandboxEventJournalService()
    e1 = svc.append("sb-1", "config.changed", {"key": "theme"}, actor="admin")
    e2 = svc.append("sb-1", "deploy.started", {"version": "1.0"})
    assert e1.sequence == 1
    assert e2.sequence == 2
    assert svc.get_sequence("sb-1") == 2


def test_get_range():
    svc = SandboxEventJournalService()
    for i in range(10):
        svc.append("sb-1", "tick", {"i": i})
    events = svc.get_range("sb-1", from_seq=5, to_seq=8)
    assert len(events) == 4
    assert events[0].sequence == 5


def test_get_by_type():
    svc = SandboxEventJournalService()
    svc.append("sb-1", "deploy", {"v": "1"})
    svc.append("sb-1", "error", {"msg": "crash"})
    svc.append("sb-1", "deploy", {"v": "2"})
    deploys = svc.get_by_type("sb-1", "deploy")
    assert len(deploys) == 2


def test_get_by_actor():
    svc = SandboxEventJournalService()
    svc.append("sb-1", "action", {}, actor="alice")
    svc.append("sb-1", "action", {}, actor="bob")
    svc.append("sb-1", "action", {}, actor="alice")
    assert len(svc.get_by_actor("sb-1", "alice")) == 2


def test_replay():
    svc = SandboxEventJournalService()
    for i in range(5):
        svc.append("sb-1", "event", {"i": i})
    replayed = svc.replay("sb-1", from_seq=3)
    assert len(replayed) == 3
    assert replayed[0].sequence == 3


def test_stats():
    svc = SandboxEventJournalService()
    svc.append("sb-1", "deploy", {})
    svc.append("sb-1", "deploy", {})
    svc.append("sb-1", "error", {})
    stats = svc.get_stats("sb-1")
    assert stats["total_events"] == 3
    assert stats["event_types"]["deploy"] == 2
