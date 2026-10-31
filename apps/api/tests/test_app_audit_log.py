"""Tests for App Audit Log — record, query by actor/resource."""

import pytest

from app.services.app_audit_log import AppAuditLog


class TestRecord:
    def test_record(self):
        a = AppAuditLog()
        e = a.record("inst-1", "e1", "alice", "create", "app", "app-1")
        assert e.action == "create"

    def test_invalid_action(self):
        a = AppAuditLog()
        with pytest.raises(ValueError):
            a.record("inst-1", "e1", "alice", "bogus", "app", "app-1")

    def test_retention(self):
        a = AppAuditLog(max_entries=3)
        for i in range(5):
            a.record("inst-1", f"e{i}", "alice", "access", "app", "app-1")
        assert a.count("inst-1") == 3


class TestQuery:
    def test_by_actor(self):
        a = AppAuditLog()
        a.record("inst-1", "e1", "alice", "create", "app", "app-1")
        a.record("inst-1", "e2", "bob", "access", "app", "app-1")
        a.record("inst-1", "e3", "alice", "update", "app", "app-1")
        assert len(a.by_actor("inst-1", "alice")) == 2

    def test_by_resource(self):
        a = AppAuditLog()
        a.record("inst-1", "e1", "alice", "create", "app", "app-1")
        a.record("inst-1", "e2", "alice", "create", "webhook", "wh-1")
        assert len(a.by_resource("inst-1", "app")) == 1

    def test_recent(self):
        a = AppAuditLog()
        for i in range(5):
            a.record("inst-1", f"e{i}", "alice", "access", "app", "app-1")
        recent = a.recent("inst-1", limit=3)
        assert len(recent) == 3
        assert recent[0].entry_id == "e4"


class TestIsolation:
    def test_cross(self):
        a = AppAuditLog()
        a.record("inst-1", "e1", "alice", "create", "app", "app-1")
        assert a.count("inst-2") == 0
