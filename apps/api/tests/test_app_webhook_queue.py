"""Tests for App Webhook Queue — enqueue, deliver, retry, dead letter."""

import pytest

from app.services.app_webhook_queue import AppWebhookQueue, DeliveryStatus


class TestEnqueue:
    def test_enqueue(self):
        q = AppWebhookQueue()
        wh = q.enqueue("inst-1", "wh1", "https://example.com/hook", '{"event":"push"}')
        assert wh.status == DeliveryStatus.QUEUED


class TestDelivery:
    def test_fifo(self):
        q = AppWebhookQueue()
        q.enqueue("inst-1", "wh1", "https://a.com", "{}")
        q.enqueue("inst-1", "wh2", "https://b.com", "{}")
        wh = q.next("inst-1")
        assert wh is not None
        assert wh.webhook_id == "wh1"

    def test_mark_delivered(self):
        q = AppWebhookQueue()
        q.enqueue("inst-1", "wh1", "https://a.com", "{}")
        q.next("inst-1")
        wh = q.mark_delivered("inst-1", "wh1")
        assert wh.status == DeliveryStatus.DELIVERED

    def test_retry(self):
        q = AppWebhookQueue()
        q.enqueue("inst-1", "wh1", "https://a.com", "{}", max_attempts=3)
        q.next("inst-1")
        wh = q.mark_failed("inst-1", "wh1", "timeout")
        assert wh.status == DeliveryStatus.QUEUED  # re-queued

    def test_dead_letter(self):
        q = AppWebhookQueue()
        q.enqueue("inst-1", "wh1", "https://a.com", "{}", max_attempts=1)
        q.next("inst-1")
        wh = q.mark_failed("inst-1", "wh1", "timeout")
        assert wh.status == DeliveryStatus.DEAD_LETTER
        assert len(q.dead_letters("inst-1")) == 1


class TestStats:
    def test_stats(self):
        q = AppWebhookQueue()
        q.enqueue("inst-1", "wh1", "https://a.com", "{}")
        q.enqueue("inst-1", "wh2", "https://b.com", "{}")
        s = q.stats("inst-1")
        assert s["queued"] == 2


class TestIsolation:
    def test_cross(self):
        q = AppWebhookQueue()
        q.enqueue("inst-1", "wh1", "https://a.com", "{}")
        assert q.queue_depth("inst-2") == 0
