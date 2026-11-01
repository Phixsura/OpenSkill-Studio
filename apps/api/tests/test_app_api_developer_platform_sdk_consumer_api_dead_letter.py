"""Tests for Consumer API Webhook Dead Letter Inspector service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_dead_letter import (
    DeadLetterInspector, DeadLetter,
)


class TestDeadLetterInspector:
    def _dl(self, lid="dl1", wid="wh1", error="timeout"):
        return DeadLetter(lid, wid, "order.created", {"id": 1}, error, "2024-01-01T00:00:00Z")

    def test_add_and_inspect(self):
        svc = DeadLetterInspector()
        svc.add(self._dl())
        result = svc.inspect("dl1")
        assert result is not None
        assert result["error"] == "timeout"

    def test_replay_success(self):
        svc = DeadLetterInspector()
        svc.add(self._dl())
        result = svc.replay("dl1", success=True)
        assert result["replayed"] is True
        assert svc.inspect("dl1")["status"] == "replayed"

    def test_replay_failure(self):
        svc = DeadLetterInspector()
        svc.add(self._dl())
        result = svc.replay("dl1", success=False)
        assert result["replayed"] is False
        assert result["attempts"] == 2

    def test_cannot_replay_non_dead(self):
        svc = DeadLetterInspector()
        svc.add(self._dl())
        svc.replay("dl1")
        result = svc.replay("dl1")
        assert result["replayed"] is False

    def test_discard(self):
        svc = DeadLetterInspector()
        svc.add(self._dl())
        svc.discard("dl1")
        assert svc.inspect("dl1")["status"] == "discarded"

    def test_replay_batch(self):
        svc = DeadLetterInspector()
        svc.add(self._dl("dl1"))
        svc.add(self._dl("dl2"))
        result = svc.replay_batch(["dl1", "dl2", "dl3"])
        assert result["replayed"] == 2
        assert result["failed"] == 1

    def test_list_dead(self):
        svc = DeadLetterInspector()
        svc.add(self._dl("dl1"))
        svc.add(self._dl("dl2"))
        svc.replay("dl2")
        dead = svc.list_dead()
        assert len(dead) == 1

    def test_list_by_webhook(self):
        svc = DeadLetterInspector()
        svc.add(self._dl("dl1", "wh1"))
        svc.add(self._dl("dl2", "wh2"))
        dead = svc.list_dead(webhook_id="wh1")
        assert len(dead) == 1

    def test_purge_discarded(self):
        svc = DeadLetterInspector()
        svc.add(self._dl("dl1"))
        svc.add(self._dl("dl2"))
        svc.discard("dl1")
        result = svc.purge_discarded()
        assert result["purged"] == 1

    def test_stats(self):
        svc = DeadLetterInspector()
        svc.add(self._dl("dl1"))
        svc.add(self._dl("dl2"))
        svc.replay("dl1")
        svc.discard("dl2")
        stats = svc.get_stats()
        assert stats["replayed"] == 1
        assert stats["discarded"] == 1

    def test_duplicate(self):
        svc = DeadLetterInspector()
        svc.add(self._dl())
        with pytest.raises(ValueError):
            svc.add(self._dl())

    def test_isolation(self):
        a, b = DeadLetterInspector(), DeadLetterInspector()
        a.add(self._dl())
        assert b.inspect("dl1") is None
