from app.services.app_marketplace_extension_access_log import AccessLogService


def test_record_and_query():
    als = AccessLogService()
    als.record("user-1", "user", "read", "/config", "ext-1", "org-1")
    als.record("user-2", "user", "write", "/config", "ext-1", "org-1")
    results = als.query(extension_id="ext-1")
    assert len(results) == 2


def test_filter_by_action():
    als = AccessLogService()
    als.record("u1", "user", "read", "/data", "ext-2", "org-1")
    als.record("u1", "user", "write", "/data", "ext-2", "org-1")
    als.record("u1", "user", "delete", "/data", "ext-2", "org-1")
    writes = als.query(extension_id="ext-2", action="write")
    assert len(writes) == 1


def test_denied_access():
    als = AccessLogService()
    als.record("u1", "user", "admin", "/settings", "ext-3", "org-1", result="denied")
    als.record("u1", "user", "read", "/data", "ext-3", "org-1")
    denied = als.get_denied_access("ext-3")
    assert len(denied) == 1
    assert denied[0].action == "admin"


def test_actor_activity():
    als = AccessLogService()
    als.record("alice", "user", "read", "/a", "ext-4", "org-1")
    als.record("alice", "user", "write", "/b", "ext-5", "org-2")
    als.record("bob", "user", "read", "/a", "ext-4", "org-1")
    alice_events = als.get_actor_activity("alice")
    assert len(alice_events) == 2


def test_stats():
    als = AccessLogService()
    als.record("u1", "user", "read", "/x", "ext-6", "org-1")
    als.record("u2", "user", "read", "/x", "ext-6", "org-1")
    als.record("u1", "user", "write", "/x", "ext-6", "org-1", result="denied")
    stats = als.get_stats("ext-6")
    assert stats["total_events"] == 3
    assert stats["by_action"]["read"] == 2
    assert stats["by_result"]["denied"] == 1
    assert stats["unique_actors"] == 2


def test_export():
    als = AccessLogService()
    als.record("u1", "user", "execute", "/run", "ext-7", "org-1")
    exported = als.export("ext-7")
    assert len(exported) == 1
    assert "event_id" in exported[0]
    assert exported[0]["action"] == "execute"
