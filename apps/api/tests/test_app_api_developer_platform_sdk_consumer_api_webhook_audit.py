"""Tests for Consumer API Webhook Audit Log service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_audit import (
    WebhookAuditLog, AuditLogEntry,
)


class TestWebhookAuditLog:
    def test_log_and_query(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        svc.log(AuditLogEntry("e2", "wh1", "enabled", "alice"))
        results = svc.query(webhook_id="wh1")
        assert len(results) == 2

    def test_query_by_action(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        svc.log(AuditLogEntry("e2", "wh1", "delivered", "system"))
        results = svc.query(action="delivered")
        assert len(results) == 1

    def test_query_by_actor(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        svc.log(AuditLogEntry("e2", "wh2", "created", "bob"))
        results = svc.query(actor="alice")
        assert len(results) == 1

    def test_webhook_history(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        svc.log(AuditLogEntry("e2", "wh1", "url_changed", "alice"))
        svc.log(AuditLogEntry("e3", "wh1", "secret_rotated", "bob"))
        history = svc.get_webhook_history("wh1")
        assert len(history) == 3

    def test_actor_activity(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        svc.log(AuditLogEntry("e2", "wh2", "deleted", "alice"))
        activity = svc.get_actor_activity("alice")
        assert len(activity) == 2

    def test_stats(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        svc.log(AuditLogEntry("e2", "wh1", "delivered", "system"))
        svc.log(AuditLogEntry("e3", "wh2", "created", "bob"))
        stats = svc.get_stats()
        assert stats["total_entries"] == 3
        assert stats["unique_webhooks"] == 2
        assert stats["unique_actors"] == 3

    def test_invalid_action(self):
        svc = WebhookAuditLog()
        with pytest.raises(ValueError):
            svc.log(AuditLogEntry("e1", "wh1", "hacked", "evil"))

    def test_eviction(self):
        svc = WebhookAuditLog()
        svc._max_entries = 10
        for i in range(15):
            svc.log(AuditLogEntry(f"e{i}", "wh1", "delivered", "sys"))
        assert svc.count() <= 10

    def test_reverse_chronological(self):
        svc = WebhookAuditLog()
        svc.log(AuditLogEntry("e1", "wh1", "created", "a", timestamp=100))
        svc.log(AuditLogEntry("e2", "wh1", "enabled", "a", timestamp=200))
        results = svc.query()
        assert results[0]["entry_id"] == "e2"  # most recent first

    def test_isolation(self):
        a, b = WebhookAuditLog(), WebhookAuditLog()
        a.log(AuditLogEntry("e1", "wh1", "created", "alice"))
        assert b.count() == 0
