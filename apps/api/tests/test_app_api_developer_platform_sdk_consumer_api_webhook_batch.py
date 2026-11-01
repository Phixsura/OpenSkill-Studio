"""Tests for Consumer API Webhook Batch Sender service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_batch import (
    WebhookBatchSender, BatchEvent,
)


class TestWebhookBatchSender:
    def test_add_and_flush(self):
        svc = WebhookBatchSender()
        svc.add_event("https://hook.com", BatchEvent("e1", "order.created", {"id": 1}))
        svc.add_event("https://hook.com", BatchEvent("e2", "order.updated", {"id": 1}))
        result = svc.flush("https://hook.com")
        assert result["flushed"] == 2

    def test_auto_flush(self):
        svc = WebhookBatchSender()
        svc.configure(max_batch_size=3)
        svc.add_event("https://hook.com", BatchEvent("e1", "a", {}))
        svc.add_event("https://hook.com", BatchEvent("e2", "b", {}))
        result = svc.add_event("https://hook.com", BatchEvent("e3", "c", {}))
        assert result["auto_flush"] is True

    def test_flush_all(self):
        svc = WebhookBatchSender()
        svc.add_event("https://a.com", BatchEvent("e1", "x", {}))
        svc.add_event("https://b.com", BatchEvent("e2", "y", {}))
        result = svc.flush_all()
        assert result["total_flushed"] == 2
        assert result["batches"] == 2

    def test_mark_sent(self):
        svc = WebhookBatchSender()
        svc.add_event("https://hook.com", BatchEvent("e1", "a", {}))
        flush = svc.flush("https://hook.com")
        result = svc.mark_sent(flush["batch_id"], 200)
        assert result["status"] == "sent"

    def test_mark_failed(self):
        svc = WebhookBatchSender()
        svc.add_event("https://hook.com", BatchEvent("e1", "a", {}))
        flush = svc.flush("https://hook.com")
        result = svc.mark_sent(flush["batch_id"], 500)
        assert result["status"] == "failed"

    def test_get_pending(self):
        svc = WebhookBatchSender()
        svc.add_event("https://hook.com", BatchEvent("e1", "a", {}))
        svc.flush("https://hook.com")
        pending = svc.get_pending()
        assert len(pending) == 1

    def test_buffer_status(self):
        svc = WebhookBatchSender()
        svc.add_event("https://a.com", BatchEvent("e1", "a", {}))
        svc.add_event("https://a.com", BatchEvent("e2", "b", {}))
        status = svc.get_buffer_status()
        assert status["total_buffered"] == 2

    def test_empty_flush(self):
        svc = WebhookBatchSender()
        result = svc.flush("https://nothing.com")
        assert result["flushed"] == 0

    def test_stats(self):
        svc = WebhookBatchSender()
        svc.add_event("https://hook.com", BatchEvent("e1", "a", {}))
        flush = svc.flush("https://hook.com")
        svc.mark_sent(flush["batch_id"], 200)
        stats = svc.get_stats()
        assert stats["sent"] == 1
        assert stats["total_events_delivered"] == 1

    def test_invalid_batch_size(self):
        svc = WebhookBatchSender()
        with pytest.raises(ValueError):
            svc.configure(max_batch_size=0)

    def test_isolation(self):
        a, b = WebhookBatchSender(), WebhookBatchSender()
        a.add_event("https://hook.com", BatchEvent("e1", "a", {}))
        assert b.get_buffer_status()["total_buffered"] == 0
