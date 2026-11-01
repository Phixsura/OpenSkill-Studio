"""Tests for Audit Trail Logger — recording, querying, hash chain, export."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.audit_trail_logger import (
    AuditAction,
    AuditOutcome,
    AuditQuery,
    AuditTrailLogger,
)


class TestRecording:
    def test_record_creates_entry(self):
        logger = AuditTrailLogger()
        entry = logger.record(
            action=AuditAction.LOGIN,
            outcome=AuditOutcome.SUCCESS,
            actor_id="user-1",
            actor_type="user",
            ip_address="192.168.1.1",
        )
        assert entry.sequence == 1
        assert entry.action == AuditAction.LOGIN
        assert entry.outcome == AuditOutcome.SUCCESS
        assert entry.actor_id == "user-1"
        assert entry.chain_hash != ""

    def test_sequence_increments(self):
        logger = AuditTrailLogger()
        e1 = logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1")
        e2 = logger.record(AuditAction.LOGOUT, AuditOutcome.SUCCESS, actor_id="u1")
        assert e2.sequence == e1.sequence + 1

    def test_chain_hashes_differ(self):
        logger = AuditTrailLogger()
        e1 = logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1")
        e2 = logger.record(AuditAction.LOGOUT, AuditOutcome.SUCCESS, actor_id="u1")
        assert e1.chain_hash != e2.chain_hash

    def test_details_stored(self):
        logger = AuditTrailLogger()
        entry = logger.record(
            AuditAction.SETTINGS_CHANGED, AuditOutcome.SUCCESS,
            actor_id="admin-1", details={"field": "name", "old": "A", "new": "B"},
        )
        assert entry.details["field"] == "name"

    def test_resource_tracking(self):
        logger = AuditTrailLogger()
        entry = logger.record(
            AuditAction.APP_CREATED, AuditOutcome.SUCCESS,
            actor_id="dev-1", resource_type="developer_app", resource_id="app-1",
        )
        assert entry.resource_type == "developer_app"
        assert entry.resource_id == "app-1"

    def test_total_entries(self):
        logger = AuditTrailLogger()
        for _ in range(5):
            logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS)
        assert logger.total_entries == 5


class TestQuerying:
    def _populate(self) -> AuditTrailLogger:
        logger = AuditTrailLogger()
        logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1", org_id="org-1")
        logger.record(AuditAction.APP_CREATED, AuditOutcome.SUCCESS, actor_id="u1",
                       resource_type="app", resource_id="app-1", org_id="org-1")
        logger.record(AuditAction.LOGIN, AuditOutcome.FAILURE, actor_id="u2", org_id="org-2")
        logger.record(AuditAction.API_KEY_CREATED, AuditOutcome.SUCCESS, actor_id="u1",
                       resource_type="api_key", resource_id="key-1", org_id="org-1")
        logger.record(AuditAction.APP_INSTALLED, AuditOutcome.DENIED, actor_id="u3", org_id="org-1")
        return logger

    def test_query_by_actor(self):
        logger = self._populate()
        results = logger.query(AuditQuery(actor_id="u1"))
        assert len(results) == 3
        assert all(e.actor_id == "u1" for e in results)

    def test_query_by_action(self):
        logger = self._populate()
        results = logger.query(AuditQuery(action=AuditAction.LOGIN))
        assert len(results) == 2

    def test_query_by_outcome(self):
        logger = self._populate()
        results = logger.query(AuditQuery(outcome=AuditOutcome.FAILURE))
        assert len(results) == 1
        assert results[0].actor_id == "u2"

    def test_query_by_org(self):
        logger = self._populate()
        results = logger.query(AuditQuery(org_id="org-1"))
        assert len(results) == 4

    def test_query_by_resource_type(self):
        logger = self._populate()
        results = logger.query(AuditQuery(resource_type="api_key"))
        assert len(results) == 1

    def test_query_limit(self):
        logger = self._populate()
        results = logger.query(AuditQuery(limit=2))
        assert len(results) == 2

    def test_query_most_recent_first(self):
        logger = self._populate()
        results = logger.query(AuditQuery())
        assert results[0].sequence > results[-1].sequence

    def test_query_time_range(self):
        logger = AuditTrailLogger()
        logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1")
        now = datetime.now(UTC)
        results = logger.query(AuditQuery(since=now - timedelta(minutes=1), until=now + timedelta(minutes=1)))
        assert len(results) == 1

    def test_combined_filters(self):
        logger = self._populate()
        results = logger.query(AuditQuery(actor_id="u1", action=AuditAction.LOGIN))
        assert len(results) == 1


class TestHashChainVerification:
    def test_valid_chain(self):
        logger = AuditTrailLogger()
        for i in range(10):
            logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id=f"u{i}")
        valid, broken_at = logger.verify_chain()
        assert valid is True
        assert broken_at is None

    def test_tampered_chain_detected(self):
        logger = AuditTrailLogger()
        for i in range(5):
            logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id=f"u{i}")
        # Tamper with middle entry
        logger._entries[2].chain_hash = "tampered_hash_value"
        valid, broken_at = logger.verify_chain()
        assert valid is False
        assert broken_at == 3  # detected at entry 3

    def test_empty_chain_valid(self):
        logger = AuditTrailLogger()
        valid, broken_at = logger.verify_chain()
        assert valid is True


class TestStats:
    def test_stats_counts(self):
        logger = AuditTrailLogger()
        logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1")
        logger.record(AuditAction.LOGIN, AuditOutcome.FAILURE, actor_id="u2")
        logger.record(AuditAction.APP_CREATED, AuditOutcome.SUCCESS, actor_id="u1")
        stats = logger.get_stats()
        assert stats.total_entries == 3
        assert stats.actions_breakdown["auth.login"] == 2
        assert stats.actions_breakdown["app.created"] == 1
        assert stats.outcomes_breakdown["success"] == 2
        assert stats.outcomes_breakdown["failure"] == 1
        assert stats.unique_actors == 2


class TestExport:
    def test_export_jsonl(self):
        logger = AuditTrailLogger()
        logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1")
        logger.record(AuditAction.LOGOUT, AuditOutcome.SUCCESS, actor_id="u1")
        export = logger.export_jsonl()
        lines = export.strip().split("\n")
        assert len(lines) == 2
        import json
        first = json.loads(lines[0])
        assert first["action"] == "auth.login"
        assert "chain_hash" in first

    def test_export_with_query(self):
        logger = AuditTrailLogger()
        logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id="u1")
        logger.record(AuditAction.APP_CREATED, AuditOutcome.SUCCESS, actor_id="u2")
        export = logger.export_jsonl(AuditQuery(actor_id="u1"))
        lines = export.strip().split("\n")
        assert len(lines) == 1


class TestRetention:
    def test_max_entries_enforced(self):
        logger = AuditTrailLogger(max_entries=5)
        for i in range(10):
            logger.record(AuditAction.LOGIN, AuditOutcome.SUCCESS, actor_id=f"u{i}")
        assert logger.total_entries == 5
        # Should have the most recent 5
        entries = logger.query(AuditQuery())
        assert entries[0].sequence == 10
