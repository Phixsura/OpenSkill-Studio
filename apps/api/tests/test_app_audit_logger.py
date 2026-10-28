"""Tests for App Audit Logger — record, query, filters, counts."""

import pytest

from app.services.app_audit_logger import AppAuditLogger, AuditSeverity


class TestRecord:
    def test_record_event(self):
        l = AppAuditLogger()
        e = l.record("inst-1", "evt-1", "user-1", "key.created",
                      "api_key", "k1", now=1000.0)
        assert e.event_id == "evt-1"
        assert e.actor == "user-1"
        assert e.action == "key.created"
        assert e.timestamp == 1000.0

    def test_with_details(self):
        l = AppAuditLogger()
        e = l.record("inst-1", "evt-1", "user-1", "config.updated",
                      "config", "c1", details="Changed timeout to 30s",
                      ip_address="10.0.0.1")
        assert e.details == "Changed timeout to 30s"
        assert e.ip_address == "10.0.0.1"

    def test_missing_actor(self):
        l = AppAuditLogger()
        with pytest.raises(ValueError, match="actor"):
            l.record("inst-1", "evt-1", "", "x", "y", "z")

    def test_missing_action(self):
        l = AppAuditLogger()
        with pytest.raises(ValueError, match="action"):
            l.record("inst-1", "evt-1", "user-1", "", "y", "z")

    def test_immutable_event(self):
        l = AppAuditLogger()
        e = l.record("inst-1", "evt-1", "user-1", "test", "r", "1")
        with pytest.raises(AttributeError):
            e.action = "modified"


class TestQuery:
    def test_basic_query(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1", now=1000.0)
        l.record("inst-1", "evt-2", "user-1", "b", "r", "2", now=1001.0)
        results = l.query("inst-1")
        assert len(results) == 2
        assert results[0].event_id == "evt-2"  # newest first

    def test_filter_by_actor(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1")
        l.record("inst-1", "evt-2", "user-2", "b", "r", "2")
        results = l.query("inst-1", actor="user-1")
        assert len(results) == 1

    def test_filter_by_action(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "key.created", "api_key", "1")
        l.record("inst-1", "evt-2", "user-1", "key.revoked", "api_key", "1")
        results = l.query("inst-1", action="key.created")
        assert len(results) == 1

    def test_filter_by_resource_type(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "api_key", "1")
        l.record("inst-1", "evt-2", "user-1", "b", "config", "1")
        results = l.query("inst-1", resource_type="config")
        assert len(results) == 1

    def test_filter_by_severity(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1", severity=AuditSeverity.INFO)
        l.record("inst-1", "evt-2", "user-1", "b", "r", "2", severity=AuditSeverity.CRITICAL)
        results = l.query("inst-1", severity=AuditSeverity.CRITICAL)
        assert len(results) == 1

    def test_filter_by_time_range(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1", now=1000.0)
        l.record("inst-1", "evt-2", "user-1", "b", "r", "2", now=2000.0)
        l.record("inst-1", "evt-3", "user-1", "c", "r", "3", now=3000.0)
        results = l.query("inst-1", since=1500.0, until=2500.0)
        assert len(results) == 1
        assert results[0].event_id == "evt-2"

    def test_query_limit(self):
        l = AppAuditLogger()
        for i in range(10):
            l.record("inst-1", f"evt-{i}", "user-1", "a", "r", str(i))
        results = l.query("inst-1", limit=3)
        assert len(results) == 3


class TestCounts:
    def test_count(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1")
        l.record("inst-1", "evt-2", "user-1", "b", "r", "2")
        l.record("inst-2", "evt-3", "user-1", "c", "r", "3")
        assert l.count("inst-1") == 2

    def test_count_by_severity(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "u", "a", "r", "1", severity=AuditSeverity.INFO)
        l.record("inst-1", "evt-2", "u", "b", "r", "2", severity=AuditSeverity.INFO)
        l.record("inst-1", "evt-3", "u", "c", "r", "3", severity=AuditSeverity.WARNING)
        counts = l.count_by_severity("inst-1")
        assert counts["info"] == 2
        assert counts["warning"] == 1
        assert counts["critical"] == 0


class TestGetEvent:
    def test_get(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1")
        e = l.get_event("inst-1", "evt-1")
        assert e.event_id == "evt-1"

    def test_not_found(self):
        l = AppAuditLogger()
        with pytest.raises(KeyError):
            l.get_event("inst-1", "nope")


class TestMaxEntries:
    def test_trims(self):
        l = AppAuditLogger(max_entries=100)
        for i in range(150):
            l.record("inst-1", f"evt-{i}", "u", "a", "r", str(i))
        assert l.count("inst-1") == 100


class TestIsolation:
    def test_cross_installation(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1")
        results = l.query("inst-2")
        assert len(results) == 0

    def test_get_event_cross_installation(self):
        l = AppAuditLogger()
        l.record("inst-1", "evt-1", "user-1", "a", "r", "1")
        with pytest.raises(KeyError):
            l.get_event("inst-2", "evt-1")
