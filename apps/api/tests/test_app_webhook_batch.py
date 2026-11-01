"""Tests for App Webhook Batch — add events, flush, delivery."""

import pytest

from app.services.app_webhook_batch import AppWebhookBatch


class TestAddEvent:
    def test_add(self):
        b = AppWebhookBatch(max_batch_size=10)
        batch = b.add_event("inst-1", "https://a.com", "e1", "push", {"ref": "main"})
        assert len(batch.events) == 1

    def test_accumulate(self):
        b = AppWebhookBatch(max_batch_size=10)
        b.add_event("inst-1", "https://a.com", "e1", "push", {})
        batch = b.add_event("inst-1", "https://a.com", "e2", "push", {})
        assert len(batch.events) == 2


class TestFlush:
    def test_auto_flush_on_max(self):
        b = AppWebhookBatch(max_batch_size=2)
        b.add_event("inst-1", "https://a.com", "e1", "push", {})
        batch = b.add_event("inst-1", "https://a.com", "e2", "push", {})
        assert batch.flushed is True

    def test_flush_ready(self):
        b = AppWebhookBatch(max_batch_size=100, flush_interval=0)
        b.add_event("inst-1", "https://a.com", "e1", "push", {})
        ready = b.flush_ready("inst-1")
        assert len(ready) == 1


class TestPending:
    def test_count(self):
        b = AppWebhookBatch(max_batch_size=100)
        b.add_event("inst-1", "https://a.com", "e1", "push", {})
        b.add_event("inst-1", "https://a.com", "e2", "push", {})
        assert b.pending_count("inst-1") == 2


class TestIsolation:
    def test_cross(self):
        b = AppWebhookBatch()
        b.add_event("inst-1", "https://a.com", "e1", "push", {})
        assert b.pending_count("inst-2") == 0
