"""Tests for App Webhook Log — record, query, success rate."""

import pytest

from app.services.app_webhook_log import AppWebhookLog


class TestRecord:
    def test_record(self):
        l = AppWebhookLog()
        e = l.record("inst-1", "l1", "push", "https://example.com", 200, 45.0)
        assert e.success is True

    def test_failure(self):
        l = AppWebhookLog()
        e = l.record("inst-1", "l1", "push", "https://example.com", 500, 120.0)
        assert e.success is False

    def test_truncate_preview(self):
        l = AppWebhookLog()
        e = l.record("inst-1", "l1", "push", "https://a.com", 200, 10, response_preview="x" * 1000)
        assert len(e.response_preview) == 500


class TestQuery:
    def test_by_status(self):
        l = AppWebhookLog()
        l.record("inst-1", "l1", "push", "https://a.com", 200, 10)
        l.record("inst-1", "l2", "push", "https://a.com", 500, 10)
        assert len(l.by_status("inst-1", True)) == 1
        assert len(l.by_status("inst-1", False)) == 1

    def test_by_event(self):
        l = AppWebhookLog()
        l.record("inst-1", "l1", "push", "https://a.com", 200, 10)
        l.record("inst-1", "l2", "issue", "https://a.com", 200, 10)
        assert len(l.by_event("inst-1", "push")) == 1

    def test_success_rate(self):
        l = AppWebhookLog()
        for _ in range(8):
            l.record("inst-1", "l", "push", "https://a.com", 200, 10)
        for _ in range(2):
            l.record("inst-1", "l", "push", "https://a.com", 500, 10)
        assert l.success_rate("inst-1") == 80.0


class TestIsolation:
    def test_cross(self):
        l = AppWebhookLog()
        l.record("inst-1", "l1", "push", "https://a.com", 200, 10)
        assert l.count("inst-2") == 0
