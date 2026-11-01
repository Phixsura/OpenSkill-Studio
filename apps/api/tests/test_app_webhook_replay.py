"""Tests for App Webhook Replay — record, replay, resolve."""

import pytest

from app.services.app_webhook_replay import AppWebhookReplay


class TestRecord:
    def test_record(self):
        r = AppWebhookReplay()
        fd = r.record_failure("inst-1", "d1", "https://a.com", "push", "{}", 500)
        assert fd.replay_count == 0


class TestReplay:
    def test_replay_success(self):
        r = AppWebhookReplay()
        r.record_failure("inst-1", "d1", "https://a.com", "push", "{}", 500)
        fd = r.replay("inst-1", "d1", 200)
        assert fd.resolved is True
        assert fd.replay_count == 1

    def test_replay_fail(self):
        r = AppWebhookReplay()
        r.record_failure("inst-1", "d1", "https://a.com", "push", "{}", 500)
        fd = r.replay("inst-1", "d1", 502)
        assert fd.resolved is False

    def test_max_replays(self):
        r = AppWebhookReplay(max_replays=2)
        r.record_failure("inst-1", "d1", "https://a.com", "push", "{}", 500)
        r.replay("inst-1", "d1", 500)
        r.replay("inst-1", "d1", 500)
        with pytest.raises(ValueError, match="Max replay"):
            r.replay("inst-1", "d1", 200)


class TestPending:
    def test_pending(self):
        r = AppWebhookReplay()
        r.record_failure("inst-1", "d1", "https://a.com", "push", "{}", 500)
        r.record_failure("inst-1", "d2", "https://a.com", "push", "{}", 502)
        r.replay("inst-1", "d1", 200)
        assert len(r.pending("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        r = AppWebhookReplay()
        r.record_failure("inst-1", "d1", "https://a.com", "push", "{}", 500)
        assert r.list_all("inst-2") == []
