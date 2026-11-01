"""Tests for Audit Trail Logger service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_audit_trail import (
    AuditTrailLogger, AuditEvent,
)


class TestAuditTrailLogger:
    def test_log_and_query(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "user1", "create", "api_key", "k1"))
        svc.log(AuditEvent("e2", "user1", "delete", "api_key", "k2"))
        results = svc.query()
        assert len(results) == 2
        assert results[0]["event_id"] == "e2"  # most recent first

    def test_hash_chain_integrity(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "u1", "create", "endpoint", "ep1"))
        svc.log(AuditEvent("e2", "u1", "update", "endpoint", "ep1"))
        svc.log(AuditEvent("e3", "u2", "delete", "endpoint", "ep2"))
        result = svc.verify_integrity()
        assert result["valid"] is True
        assert result["checked"] == 3

    def test_tamper_detection(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "u1", "create", "key", "k1"))
        svc.log(AuditEvent("e2", "u1", "update", "key", "k1"))
        # Tamper with entry
        svc._entries[0].hash = "tampered"
        result = svc.verify_integrity()
        assert result["valid"] is False

    def test_query_by_actor(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "alice", "create", "key", "k1"))
        svc.log(AuditEvent("e2", "bob", "create", "key", "k2"))
        results = svc.query(actor_id="alice")
        assert len(results) == 1
        assert results[0]["actor_id"] == "alice"

    def test_query_by_action(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "u1", "create", "ep", "ep1"))
        svc.log(AuditEvent("e2", "u1", "delete", "ep", "ep2"))
        results = svc.query(action="delete")
        assert len(results) == 1

    def test_get_entry(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "u1", "create", "key", "k1"))
        entry = svc.get_entry(1)
        assert entry is not None
        assert entry["event_id"] == "e1"
        assert svc.get_entry(99) is None

    def test_stats(self):
        svc = AuditTrailLogger()
        svc.log(AuditEvent("e1", "u1", "create", "key", "k1"))
        svc.log(AuditEvent("e2", "u2", "create", "key", "k2"))
        svc.log(AuditEvent("e3", "u1", "delete", "key", "k1"))
        stats = svc.get_stats()
        assert stats["total_entries"] == 3
        assert stats["unique_actors"] == 2
        assert stats["action_counts"]["create"] == 2

    def test_empty_action_rejected(self):
        svc = AuditTrailLogger()
        with pytest.raises(ValueError):
            svc.log(AuditEvent("e1", "u1", "", "key", "k1"))

    def test_isolation(self):
        a, b = AuditTrailLogger(), AuditTrailLogger()
        a.log(AuditEvent("e1", "u1", "create", "key", "k1"))
        assert b.query() == []
