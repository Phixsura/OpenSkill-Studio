"""Tests for App Webhook Replay — queue, replay, retry, succeed/fail."""

import pytest

from app.services.app_webhook_replay import AppWebhookReplay, ReplayStatus


class TestQueue:
    def test_queue(self):
        r = AppWebhookReplay()
        req = r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com/hook", '{"data":1}')
        assert req.status == ReplayStatus.QUEUED
        assert req.attempt == 0

    def test_duplicate(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}")
        with pytest.raises(ValueError, match="already exists"):
            r.queue_replay("inst-1", "rp-1", "evt-2", "https://x.com", "{}")


class TestReplay:
    def test_start(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}")
        req = r.start_replay("inst-1", "rp-1")
        assert req.status == ReplayStatus.REPLAYING
        assert req.attempt == 1

    def test_succeed(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}")
        r.start_replay("inst-1", "rp-1")
        req = r.succeed_replay("inst-1", "rp-1")
        assert req.status == ReplayStatus.SUCCEEDED

    def test_fail_retry(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}", max_attempts=3)
        r.start_replay("inst-1", "rp-1")
        req = r.fail_replay("inst-1", "rp-1", "timeout")
        assert req.status == ReplayStatus.QUEUED  # re-queued

    def test_fail_exhausted(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}", max_attempts=1)
        r.start_replay("inst-1", "rp-1")
        req = r.fail_replay("inst-1", "rp-1", "error")
        assert req.status == ReplayStatus.FAILED


class TestList:
    def test_filter_status(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}")
        r.queue_replay("inst-1", "rp-2", "evt-2", "https://x.com", "{}")
        r.start_replay("inst-1", "rp-1")
        r.succeed_replay("inst-1", "rp-1")
        queued = r.list_replays("inst-1", status=ReplayStatus.QUEUED)
        assert len(queued) == 1


class TestIsolation:
    def test_cross_installation(self):
        r = AppWebhookReplay()
        r.queue_replay("inst-1", "rp-1", "evt-1", "https://x.com", "{}")
        with pytest.raises(KeyError):
            r._get("inst-2", "rp-1")
